import socket
import urllib.parse
from .http_conn import *
from .logconfig import get_logger


class HTTPProxyHandler(HTTPHandler):
    def __init__(self, client_sock: socket) -> None:
        super().__init__(client_sock)
        self.logger = get_logger("PROXY")
        
        self.keep_alive = None
        self.request = None
        
    def handle(self):
        logger = self.logger
        peername = get_peer_addr(self.client_sock)
        
        self.logger.debug(f"handle request from {peername}")
        
        try:
            self.keep_alive = True
            while self.keep_alive:
                logger.debug(f"parse request")
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
        
        logger.debug(f"end connection from {peername}")
        self.client_sock.close()
    
    def handle_connect(self):
        req = self.request
        logger = self.logger
        client_sock = self.client_sock
        
        logger.debug(f"handle CONNECT request")
        
        self.keep_alive = False
        
        hostname, port = req.uri.split(":")
        port = int(port)
        try:
            server_sock = socket.create_connection((hostname, port))
        except Exception as e:
            logger.error(f"failed to connect to {hostname}:{port}")
            logger.error(e)
            res = HTTPResponse("HTTP/1.1", 502, "Bad Gateway")
            res.headers["Connection"] = "close"
            res.send(client_sock)
            client_sock.sendall(str(e).encode("utf-8"))
            return
        
        res = HTTPResponse("HTTP/1.1", 200, "Connection Established")
        res.headers["Connection"] = "close"
        res.send(client_sock)
        
        relay_sock(client_sock, server_sock)
        
        
    
    def handle_normal(self):
        req = self.request
        logger = self.logger
        client_sock = self.client_sock
        
        proxy_connection = req.headers["Proxy-Connection"].lower()
        if proxy_connection == "keep-alive":
            self.keep_alive = True
        else:
            self.keep_alive = False
        
        logger.info(f"proxy to {req.uri}")
        server_sock = create_http_socket(req.uri)
        
        # construct request headers
        headers = req.headers.copy()
        
        # remove proxy headers
        pop_headers = []
        for k, v in headers:
            if k.startswith("Proxy-"):
                pop_headers.append(k)
        for k in pop_headers:
            headers.pop(k)
            
        # add connection header
        headers["Connection"] = "close"
        
        # send request
        req = HTTPRequest()
        req.method = "GET"
        url = urllib.parse.urlparse(req.uri)
        req.uri = url.path
        req.protocol = "HTTP/1.1"
        req.headers = headers
        
        logger.debug(f"send request to server")
        logger.debug(f" > {req.method} {req.uri} {req.protocol}")
        for k, v in req.headers:
            logger.debug(f" > {k}: {v}")
        
        req.send(server_sock)
        
        if req.has_body():
            chunked = "chunked" in req.headers["Transfer-Encoding"].lower()
            req_body = HTTPBody(req.headers, client_sock)
            
            logger.debug(f"send request body to server, chunked={chunked}")
            relay_body(req_body, server_sock, chunked=chunked)
        logger.debug(f"finish sending request")
        
        # receive response
        logger.debug(f"receiving response from server")
        server_res = HTTPResponse()
        server_res.parse(server_sock)
        logger.debug(f" < {server_res.protocol} {server_res.status_code} {server_res.status}")
        for k, v in server_res.headers:
            logger.debug(f" < {k}: {v}")
        
        res = server_res.copy()
        res.headers["Connection"] = "keep-alive" if self.keep_alive else "close"
        
        # TODO: 
        # handle unexpected response when server forgets to send content-length
        # and not sending chunked encoding
        
        logger.debug(f"relaying response headers to client")
        res.send(client_sock)
        
        logger.debug(f"relaying response body to client")
        res_body = HTTPBody(server_res.headers, server_sock)
        relay_body(res_body, client_sock, chunked="chunked" in res.headers["Transfer-Encoding"].lower())


