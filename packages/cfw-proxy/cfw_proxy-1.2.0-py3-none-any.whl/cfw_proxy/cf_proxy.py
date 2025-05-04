from .certmgr import CertCache
from .http_conn import *
import socket
import urllib.parse

class CloudflareProxy(HTTPHandler):
    STATUS_CODES_WITHOUT_BODY = (100, 101, 102, 103, 204, 205, 304)

    def __init__(self, client_sock: socket.socket, **kwargs):
        super().__init__(client_sock)
        self.logger = get_logger("CF")
        
        self.cert_cache = kwargs.get("cert_cache", CertCache())
        self.cf_url = kwargs.get("cf_url", "https://www.cloudflare.com")
        self.cf_auth = kwargs.get("cf_auth", "hello authencation")
        self.cf_host = urllib.parse.urlparse(self.cf_url).hostname
        
        self.keep_alive = None
        self.request = None

    def handle(self):
        logger = self.logger
        peername = get_peer_addr(self.client_sock)
        
        logger.info(f"handling request from {peername} via {self.cf_url}")
        
        try:
            self.keep_alive = True
            while self.keep_alive:
                logger.info(f"waiting for request")
                req = HTTPRequest()
                req.parse(self.client_sock)
                self.request = req
                
                if req.method == "CONNECT":
                    self.handle_connect()
                else:
                    self.handle_normal()
                    
                self.request = None
        except HTTPConnectionClosed:
            pass
            
        logger.info(f"end connection from {peername}")
        self.client_sock.close()
    
    def handle_connect(self):
        # response with not support yet
        req = self.request
        logger = self.logger
        client_sock = self.client_sock
        
        logger.info(f"receive CONNECT request {req.method} {req.uri} {req.protocol}")
        req.headers.log(logger, prefix=" C>P ")
        
        netloc = req.uri
        hostname, port = netloc.split(":")
        port = int(port)
        
        # response with not support yet
        logger.info(f"ack with 200, connection established")
        connect_succ = HTTPResponse("HTTP/1.1", 200, "Connection Established")
        connect_succ.headers["Connection"] = "close"
        self.keep_alive = False
        connect_succ.send(client_sock)
        
        # MITM attack
        logger.info(f"create MITM socket to client")
        try:
            crt_file, key_file = self.cert_cache.get_cert(hostname)
            MITM_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            MITM_ctx.load_cert_chain(crt_file, key_file)
            MITM_sock = MITM_ctx.wrap_socket(client_sock, server_side=True)
        except Exception as e:
            logger.exception(f"failed to create MITM socket, {e}")
            return
        
        logger.info(f"handling request from MITM socket")
        cf_host = urllib.parse.urlparse(self.cf_url).hostname
        try:
            while True:
                req = HTTPRequest()
                req.parse(MITM_sock)
                logger.info(f"get request: {req.method} {req.uri} {req.protocol}")
                req.headers.log(logger, prefix=" C>P ")

                # special = req.uri.startswith('/v2/gurucomputing/headscale-ui/manifests/')
                special = False
                if special:
                    logger.error(f"special request: ")
                    logger.error(f" C>P {req.method} {req.uri} {req.protocol}")
                    req.headers.log(logger, prefix=" C>P ", level=logging.ERROR)
                
                if req.method == "CONNECT":
                    logger.info(f"reject CONNECT, not support yet")
                    resp = HTTPResponse.method_not_allowed()
                    resp.send(MITM_sock)
                    break
                
                if "Upgrade" in req.headers:
                    logger.info(f"reject upgrade request, not support yet")
                    resp = HTTPResponse.bad_request()
                    resp.send(MITM_sock)
                    MITM_sock.sendall(b"Upgrade not support yet")
                    break
                
                # modify request headers
                pxy_req = self.modify_req_headers(req, cf_host)
                request_url = urllib.parse.urljoin("https://" + netloc, req.uri)
                pxy_req.uri = '/proxy/' + request_url
                
                # send request to cloudflare
                cf_sock = create_http_socket(self.cf_url)
                logger.info(f"sending request to {self.cf_url}")
                logger.debug(f" P>S {pxy_req.method} {pxy_req.uri} {pxy_req.protocol}")
                pxy_req.headers.log(logger, prefix=" P>S ")
                pxy_req.send(cf_sock)
                
                if req.has_body():
                    logger.info(f"request has body, sending")
                    chunked = "chunked" in req.headers["Transfer-Encoding"].lower()
                    req_body = HTTPBody(req.headers, MITM_sock)
                    relay_body(req_body, cf_sock, chunked)
                    logger.info(f"sending request body done")
                
                # receive response from cloudflare
                logger.info(f"receiving response")
                cf_resp = HTTPResponse()
                cf_resp.parse(cf_sock)
                
                logger.info(f"response: {cf_resp.protocol} {cf_resp.status_code} {cf_resp.status}")
                cf_resp.headers.log(logger, prefix=" P<S ")

                if special:
                    logger.error(f"special response: ")
                    logger.error(f" P<S {cf_resp.protocol} {cf_resp.status_code} {cf_resp.status}")
                    cf_resp.headers.log(logger, prefix=" P<S ", level=logging.ERROR)
                
                # modify response
                pxy_resp = cf_resp.copy()
                del_hdr = ["Connection", "Keep-Alive"]
                for k in del_hdr:
                    if k in pxy_resp.headers:
                        del pxy_resp.headers[k]
                pxy_resp.headers["Connection"] = "Keep-Alive"
                
                logger.info(f"sending response to client")
                pxy_resp.headers.log(logger, prefix=" C<P ")
                pxy_resp.send(MITM_sock)
                
                if cf_resp.status_code not in self.STATUS_CODES_WITHOUT_BODY:
                    logger.info(f"sending response body to client")
                    res_body = HTTPBody(cf_resp.headers, cf_sock)
                    relay_body(res_body, MITM_sock, res_body.chunked())
                    logger.info(f"sending response body done")
                
                cf_sock.close()
        except HTTPConnectionClosed:
            pass
        except Exception as e:
            logger.exception(f"error during MITM, {e}")
            
        MITM_sock.close()
        
    def handle_normal(self):
        req = self.request
        logger = self.logger
        client_sock = self.client_sock
        
        logger.info(f"get HTTP request {req.method} {req.uri} {req.protocol}")
        req.headers.log(logger, prefix=" C>P ")
        
        if "Upgrade" in req.headers:
            logger.info(f"reject, 'Upgrade' not support yet")
            resp = HTTPResponse.bad_request()
            resp.send(client_sock)
            client_sock.sendall(b"Upgrade not support yet")
            self.keep_alive = False
            return
                
        # set keep-alive
        self.keep_alive = "keep-alive" in req.headers["Proxy-Connection"].lower()
        
        # get proxy hostname and port
        url = urllib.parse.urlparse(req.uri)
        hostname = url.hostname or req.headers["Host"]
        
        # modify request headers
        pxy_req = self.modify_req_headers(req, hostname)
        pxy_req.uri = '/proxy/' + req.uri
        
        # send request to cloudflare
        cf_sock = create_http_socket(self.cf_url)
        logger.info(f"send to {self.cf_url}, {pxy_req.method} {pxy_req.uri} {pxy_req.protocol}")
        logger.debug(f" P>S {pxy_req.method} {pxy_req.uri} {pxy_req.protocol}")
        pxy_req.headers.log(logger, prefix=" P>S ")
        pxy_req.send(cf_sock)
        
        if req.has_body():
            logger.info(f"request has body, sending")
            chunked = "chunked" in req.headers["Transfer-Encoding"].lower()
            req_body = HTTPBody(req.headers, client_sock)
            relay_body(req_body, cf_sock, chunked)
            logger.info(f"request body sent")

        # receive response from cloudflare
        logger.info(f"receiving response")
        server_res = HTTPResponse()
        server_res.parse(cf_sock)
        
        logger.info(f"response: {server_res.protocol} {server_res.status_code} {server_res.status}")
        server_res.headers.log(logger, prefix=" P<S ")
        
        # modify response
        pxy_res = server_res.copy()
        pxy_res.headers["Connection"] = "keep-alive" if self.keep_alive else "close"
        
        logger.info(f"sending response to client")
        logger.debug(f" C<P {pxy_res.protocol} {pxy_res.status_code} {pxy_res.status}")
        pxy_res.headers.log(logger, prefix=" C<P ")
        pxy_res.send(client_sock)
        
        if pxy_res.status_code not in self.STATUS_CODES_WITHOUT_BODY:
            logger.info(f"sending response body to client")
            res_body = HTTPBody(pxy_res.headers, cf_sock)
            relay_body(res_body, client_sock, res_body.chunked())

        logger.info(f"HTTP request proxy done")
    
    def modify_req_headers(self, old_req: HTTPRequest, host: str):
        old_hdr = old_req.headers

        req = old_req.copy()
        del_hdr = ["Proxy-Connection", "Connection", "Keep-Alive"]
        for k in del_hdr:
            if k in req.headers:
                del req.headers[k]
        
        items = list(req.headers.items())
        req.headers.clear()
        for k, v in items:
            req.headers.add(CFW_PROXY_ESCAPE_PREFIX + k, v)
        
        req.headers["Connection"] = "close"
        req.headers["Host"] = self.cf_host
        req.headers["PCFP-Authentication"] = self.cf_auth

        if "Transfer-Encoding" in old_hdr and old_hdr["Transfer-Encoding"].lower() == "chunked":
            req.headers["Transfer-Encoding"] = old_hdr["Transfer-Encoding"]
        elif "Content-Length" in old_hdr:
            req.headers["Content-Length"] = old_hdr["Content-Length"]
        elif req.method in ["GET", "HEAD", "DELETE"]:
            pass # GET request has no body, do nothing
        else:
            logger = get_logger("CF")
            logger.error(f"no content length or transfer encoding, bellow is the request")
            logger.error(f" C>P {old_req.method} {old_req.uri} {old_req.protocol}")
            old_req.headers.log(logger, prefix=" C>P ", level=logging.ERROR)
            # raise ValueError("no content length or transfer encoding")

        return req