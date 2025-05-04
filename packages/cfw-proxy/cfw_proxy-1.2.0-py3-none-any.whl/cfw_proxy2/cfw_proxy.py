import socket
import ssl
import threading
from typing import Tuple

from cfw_proxy2.http_conn import ConnClosed, ConnType, HTTPRequest, HTTPResponse, patch_ssl_socket
from .http_client import HttpClientPool
import queue
from pydantic import BaseModel
from .certmgr import CertCache
from copy import deepcopy
import urllib.parse
import time
from loguru import logger

class CFWProxyConfig(BaseModel):
    listen_addr: Tuple[str, int] = ("127.0.0.1", 8843)

    ca_cert: str
    ca_key: str
    cert_cachedir: str

    timeout: float = 5
    client_idle_timeout: float = 30

    worker_count: int = 100

    cfw_pool_size: int = 10
    cfw_host: str
    cfw_key: str
    cfw_header_prefix: str = "PCFP-X-"

class RelayTask:
    request: HTTPRequest
    response: HTTPResponse
    end_after_this_task: bool = False

    def __init__(self) -> None:
        self.request = None
        self.response = None
        self.end_after_this_task = False

class _RelayLoop:
    def __init__(
            self, 
            client_sock: ConnType, 
            cfw_config: CFWProxyConfig,
            cfw_conn_pool: HttpClientPool,
            cert_cache: CertCache,
            treat_connect_as_tls: bool = False,
        ):

        self.client_sock = client_sock
        self.cfw_config = cfw_config
        self.cert_cache = cert_cache
        self.cfw_conn_pool = cfw_conn_pool
        self.treat_connect_as_tls = treat_connect_as_tls

    def run_loop(self):
        self.client_sock.setblocking(True)
        self.client_sock.settimeout(self.cfw_config.timeout)


        last_request_time = time.monotonic()
        while True:
            logger.debug("Waiting for request")
            try:
                req = HTTPRequest.parse(self.client_sock)
                last_request_time = time.monotonic()
            except ConnClosed:
                logger.debug("Client closed the connection")
                break # Client closed the connection
            except TimeoutError:
                cur_time = time.monotonic()
                if cur_time - last_request_time > self.cfw_config.client_idle_timeout:
                    logger.debug("Client idle timeout, closing connection")
                    break
                else:
                    logger.debug("No request received within timeout, continue")
                    continue # Timeout

            relay_task = RelayTask()
            relay_task.request = req

            logger.info(f"Received request: {req.method} {req.uri}")
            logger.debug(f"Request headers: {req.headers}")

            if "Upgrade" in req.headers:
                logger.debug("Reject all Upgrade requests")
                self.reject_upgrade_request(relay_task)
            elif req.method != "CONNECT":
                logger.debug("Relay non-CONNECT request")
                self.relay_non_connect_request(relay_task)
                logger.debug("Response status: {relay_task.response.status_code}")
                logger.debug("Response headers: {relay_task.response.headers}")
            elif self.treat_connect_as_tls:
                logger.debug("Got CONNECT request, treat it as TLS and relay")
                self.handle_connect_as_tls(relay_task)
            else:
                logger.debug("Reject the request as its HTTP method is not supported")
                self.reject_unsupported_methods(relay_task)

            logger.debug(f"End after the current task: {relay_task.end_after_this_task}")
            if relay_task.end_after_this_task:
                break

    def handle_connect_as_tls(self, task: RelayTask):
        target_hostname, port = task.request.uri.split(":")
        port = int(port)

        if port != 443:
            res = HTTPResponse.bad_request()
            task.response = res
            task.end_after_this_task = True
            res.send(self.client_sock)
            return

        ## Deceive the client that the connection is established
        ## so that the proxy plays the role of a man-in-the-middle attacker.
        connect_succ_resp = HTTPResponse(
            protocol="HTTP/1.1",
            status_code=200,
            reason="Connection Established"
        )
        connect_succ_resp.related_request = HTTPResponse.PseudoRelatedRequest()
        connect_succ_resp.headers.set("Connection", "close")
        connect_succ_resp.headers.set("Content-Length", "0")
        connect_succ_resp.send(self.client_sock)

        decrypted_sock = None
        try:
            cert_file, key_file = self.cert_cache.get_cert(target_hostname)
            MITM_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            MITM_ctx.load_cert_chain(cert_file, key_file)
            decrypted_sock = MITM_ctx.wrap_socket(self.client_sock, server_side=True)
            decrypted_sock = patch_ssl_socket(decrypted_sock)
        except Exception as e:
            logger.error(f"Error while handling CONNECT as TLS: {e}")

            task.end_after_this_task = True
            if decrypted_sock is not None:
                decrypted_sock.close()
            return
        
        ## Create a new handler
        loop = _RelayLoop(
            client_sock=decrypted_sock, 
            cfw_config=self.cfw_config, 
            cfw_conn_pool=self.cfw_conn_pool, 
            cert_cache=self.cert_cache,
            treat_connect_as_tls=False
        )
        loop.run_loop()
        task.end_after_this_task = True
    

    def reject_upgrade_request(self, task: RelayTask):
        res = HTTPResponse.bad_request()
        task.response = res
        task.end_after_this_task = True

        res.send(self.client_sock)

    def relay_non_connect_request(self, task: RelayTask):
        req = task.request

        ## Create a new request to send to CFW
        modified_req = HTTPRequest()
        modified_req.method = req.method
        modified_req.protocol = req.protocol

        # Set modified URI
        # - for decrypted HTTPS requests, the URI should be the 
        #   concatenation of the value of the "Host" header and the
        #   original URI.
        # - for plain-text HTTP requests, the URI should be the
        #   original URI.
        if req.uri.lower().startswith("/"): # decrypted HTTPS
            target_url = urllib.parse.urljoin(
                "https://" + req.headers.get("Host"),
                req.uri
            )
            modified_req.uri = "/proxy/" + target_url
        else: # plain-text HTTP
            modified_req.uri = "/proxy/" + req.uri

        # Prefix original headers with cfw header prefix
        for k in req.headers.keys():
            if k in ["Proxy-Connection", "Connection", "Keep-Alive"]:
                continue
            modified_req.headers.set(
                self.cfw_config.cfw_header_prefix + k, 
                deepcopy(req.headers.get(k))
            )

        # Always try to keep proxy-cfw connection alive
        modified_req.headers.set("Connection", "keep-alive")

        # Set host and authentication headers
        modified_req.headers.set("Host", self.cfw_config.cfw_host)
        modified_req.headers.set("PCFP-Authentication", self.cfw_config.cfw_key)

        # Ensure that there is a definite content boundary.
        # In other words, the boundary is not EOF.
        if req.method not in HTTPRequest.MTH_MAY_HAVE_BODY:
            # These methods do not have a body.
            # No check is needed
            pass
        elif "Content-Length" in req.headers:
            modified_req.headers.set("Content-Length", req.headers.get("Content-Length"))
        elif (
            "Transfer-Encoding" in req.headers and 
            req.headers.get("Transfer-Encoding").lower() == "chunked"
        ):
            modified_req.headers.set("Transfer-Encoding", req.headers.get("Transfer-Encoding"))
        else:
            res = HTTPResponse.bad_request()
            task.response = res
            task.end_after_this_task = True
            
            error_text = "Missing Content-Length or Transfer-Encoding header".encode()
            res.headers.set("Content-Length", len(error_text))
            res.headers.set("Content-Type", "text/plain")
            s1, s2 = socket.socketpair()
            s1.send(error_text)
            res.reset_body(s2)

            res.send(self.client_sock)
            return
        
        ## Set the modified request body
        modified_req.reset_body(req._body_stream)
        
        ## Relay the request to CFW
        with self.cfw_conn_pool.get_client(timeout=10) as cfw_conn:
            if cfw_conn is None:
                # CFW connection pool is empty
                res = HTTPResponse.service_unavailable()
                task.response = res
                task.end_after_this_task = True
                res.send(self.client_sock)
                return
            
            with cfw_conn.send_request(modified_req) as cfw_res:
                ## Create a new response to send to the client
                modified_res = HTTPResponse()
                modified_res.protocol = cfw_res.protocol
                modified_res.status_code = cfw_res.status_code
                modified_res.reason = cfw_res.reason
                modified_res.headers = cfw_res.headers.copy()
                modified_res.related_request = modified_req
                modified_res.reset_body(cfw_res._body_stream)

                ## Save to the task
                task.response = modified_res

                ## Modify the response headers
                # TODO: 必须全部覆盖为 close 才能正常工作。不然会有一堆 worker卡
                # 在等待客户端发送请求的状态。导致无法处理新的请求。但设置为
                # close 会导致客户端无法复用到本代理服务的 HTTP 连接，但也确实能
                # 正常上网。这个问题需要进一步研究。
                modified_res.headers.set("Connection", "close")

                ## Relay the response to the client
                modified_res.send(self.client_sock)

                cfw_res._body_consumed = True
        


    def reject_unsupported_methods(self, task: RelayTask):
        res = HTTPResponse.method_not_allowed(
            allowed_methods=[
                "GET", "POST", "PUT", 
                "HEAD", "DELETE", "OPTIONS", 
                "PATCH", "TRACE"
            ]
        )
        task.response = res
        task.end_after_this_task = True

        res.send(self.client_sock)


class CFWProxyServer:
    def __init__(
            self, 
            config: CFWProxyConfig
        ):
        self.config = config
        self.listen_sock = socket.create_server(
            config.listen_addr, 
        )

        self._worker_tokens = None
        self._serving = False
        self._cfw_conn_pool = HttpClientPool(
            config.cfw_host, 
            https=True, 
            pool_size=config.cfw_pool_size
        )
        self._cert_cache = CertCache(
            cache_dir=self.config.cert_cachedir,
            cafile=self.config.ca_cert,
            cakey=self.config.ca_key
        )

    def serve_forever(self):
        self._serving = True
        self._worker_tokens = queue.Queue()
        for i in range(self.config.worker_count):
            self._worker_tokens.put(f"W{i}")

        logger.info(f"CFW Proxy server started at {self.config.listen_addr}")
        while self._serving:
            self.listen_sock.settimeout(1)
            try:
                sock, addr = self.listen_sock.accept()
            except socket.timeout:
                # logger.trace("Timeout on waiting for a new connection, continue")
                continue # Timeout

            try:
                # worker_token = self._worker_tokens.get_nowait()
                worker_token = self._worker_tokens.get()
            except queue.Empty:
                logger.info(f"Rejecting connection from {addr} as no worker available")
                self.quick_reject(sock)
                continue
            
            logger.info(f"Accepted connection from {addr} to worker {worker_token}")
            worker = threading.Thread(
                target=self._worker_wrapper,
                args=(sock, worker_token)
            )
            worker.start()
    
    def _worker_wrapper(self, sock: socket.socket, worker_token: str):
        cur_thread = threading.current_thread()
        cur_thread.name = f"{worker_token}"
        logger.info("started")
        try:
            loop = _RelayLoop(
                client_sock=sock,
                cfw_config=self.config,
                cfw_conn_pool=self._cfw_conn_pool,
                cert_cache=self._cert_cache,
                treat_connect_as_tls=True
            )
            loop.run_loop()
        except Exception:
            logger.exception("Unknown error captured by master")
        finally:
            sock.close()
            self._worker_tokens.put(worker_token)

    
    def quick_reject(self, sock: socket.socket):
        try:
            sock.settimeout(3)

            resp = HTTPResponse.service_unavailable()
            resp.send(sock)
        except Exception:
            logger.exception("Error while rejecting connection")
        finally:
            sock.close()

