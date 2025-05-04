import contextlib
import socket
import ssl
import threading
import queue

from cfw_proxy2.http_conn import ConnClosed, HTTPRequest, HTTPResponse, patch_ssl_socket

class HttpClient:
    def __init__(self, hostname, port=None, https: bool = True, timeout: float | None = 10):
        self.hostname = hostname
        self.https = https
        self.port = port or (443 if https else 80)
        self.timeout = timeout

        try:
            self.sock = socket.create_connection((self.hostname, self.port))
            if self.https:
                ctx = ssl.create_default_context()
                self.sock = ctx.wrap_socket(self.sock, server_hostname=self.hostname)
                self.sock = patch_ssl_socket(self.sock)
                self.sock.settimeout(self.timeout)
        except:
            self.sock = None
            raise
    
    @contextlib.contextmanager
    def send_request(self, req: HTTPRequest):
        """
        Send a request and return the response wrapped in a context manager.

        Make sure to read all the response body before the context manager
        exits.
        """
        if self.sock is None:
            raise ConnClosed("Connection is closed")

        self._during_request = True
        try:
            req.send(self.sock)
            resp = HTTPResponse.parse(self.sock)
            resp.related_request = req
            yield resp

            if resp.headers.get("Connection") == "close":
                self.sock.close()
                self.sock = None
            
            if (
                resp.status_code not in HTTPResponse.STATUS_CODES_WITHOUT_BODY
                and resp._body_consumed is False
            ):
                raise ValueError("Response body not consumed")
        except Exception as e:
            # print(f"{threading.current_thread().name} error: {type(e)}, {e}")
            self.sock = None
            raise e

    def close(self):
        if self.sock is not None: 
            self.sock.close()
            self.sock = None


class HttpClientPool:
    def __init__(
            self, 
            hostname, 
            port=None, 
            https: bool = True, 
            pool_size: int = 5,
            timeout: float | None = 10
        ):
        self.hostname = hostname
        self.https = https
        self.port = port or (443 if https else 80)
        self.pool_size = pool_size
        self.timeout = timeout

        self.idle_clients = queue.Queue()
        self.client_count = 0
        self.lock = threading.Lock()

    @contextlib.contextmanager
    def get_client(self, timeout: float | None = 10):
        timeout = timeout if timeout is not None else self.timeout

        client = None
        create_new = False
        try:
            client = self.idle_clients.get_nowait()
        except queue.Empty:
            with self.lock:
                if self.client_count < self.pool_size:
                    create_new = True
                    self.client_count += 1

        try:
            if client is not None: # Reuse existing client
                # print(f"{threading.current_thread().name} reusing client {client.sock.fileno()}")
                yield client
            elif create_new:       # Pool is not full, and create a new client
                client = HttpClient(
                    self.hostname, 
                    self.port, 
                    self.https,
                    timeout=timeout
                )
                # print(f"{threading.current_thread().name} create new connection {client.sock.fileno()}")
                yield client
            else:                  # Pool is full, wait for a client to be available
                try: 
                    client = self.idle_clients.get(timeout=timeout)
                except queue.Empty: 
                    client = None
                # print(f"{threading.current_thread().name} waiting result {None if client is None else client.sock.fileno()}")
                yield client        # Return None to indicate the timeout
        finally:
            if client is None:      # No client was allocated, do nothing
                # NOTE: DO NOT USE `return` to replace `pass` here, it will
                # cause the context manager to skip everythin in the `with`
                # block when `client` is None.
                pass
            elif client.sock is None: # Client was closed
                with self.lock:
                    # print(f"{threading.current_thread().name} closed the connection")
                    self.client_count -= 1
            else:
                # print(f"{threading.current_thread().name} put the client to idle: {client.sock.fileno()}")
                self.idle_clients.put(client)
