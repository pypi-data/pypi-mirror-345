import socket
import io
from typing import Iterable
import urllib.parse
import threading
from .logconfig import get_logger
import ssl
import logging
from copy import deepcopy
import itertools

class HTTPConnectionClosed(Exception): pass

def readline(sock: socket.socket):
    line = b''
    while True:
        data = sock.recv(1)
        if not data: 
            raise HTTPConnectionClosed()
        if data == b'\n':
            break
        line += data
    line = line.decode('utf-8').strip()
    return line


def send_chunk(sock: socket.socket, data: bytes):
    sock.sendall(f"{hex(len(data))[2:]}\r\n".encode())
    sock.sendall(data)
    sock.sendall(b"\r\n")
    

def create_http_socket(url: str):
    url = urllib.parse.urlparse(url)
    if url.scheme == "http":
        sock = socket.create_connection((url.hostname, url.port or 80))
    elif url.scheme == "https":
        sock = socket.create_connection((url.hostname, url.port or 443))
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=url.hostname)
    else:
        raise Exception("Unsupported protocol")
    return sock


def relay_body(src: "HTTPBody", dst: socket.socket, chunked=False):
    if chunked:
        for data in src.itr_data():
            send_chunk(dst, data)
        send_chunk(dst, b"")
    else:
        for data in src.itr_data():
            dst.sendall(data)



def relay_sock(src: socket.socket, dst: socket.socket):
    timeout = 0.01
    src.settimeout(timeout)
    dst.settimeout(timeout)
    
    # increase buffer size to improve performance
    bufsz = 64 * 1024
    
    readable = [src, dst]
    
    try:
        while True:
            if not readable: break
            if src in readable:
                try:
                    data = src.recv(bufsz)
                    if not data: 
                        readable.remove(src)
                    dst.sendall(data)
                except socket.timeout:
                    pass
            if dst in readable:
                try:
                    data = dst.recv(bufsz)
                    if len(data) == 0:
                        readable.remove(dst)
                    src.sendall(data)
                except socket.timeout:
                    pass
    except Exception as e:
        get_logger("RLY SOCK").error(e)
            

def get_peer_addr(sock: socket.socket) -> str:
    peername = sock.getpeername()
    return f"{peername[0]}:{peername[1]}"

# Note: should be exactly same as the prefix defined in Cloudflare worker script
CFW_PROXY_ESCAPE_PREFIX = "PCFP-X-"
class Headers:
    REPEATABLE_HEADERS = list(itertools.chain.from_iterable([
        [h.lower(), f"{CFW_PROXY_ESCAPE_PREFIX.lower()}{h}"] 
        for h in [
            "Set-Cookie", 
            "Cookie",
            "Warning",
            "WWW-Authenticate",
            "Proxy-Authenticate",
            "Proxy-Authentication",
            "Accept",
            "Accept-Patch",
            "Accept-Ranges",
            "Vary",
            "Link",
            "Allow",
            "Content-Encoding",
            "Content-Language",
            "Via"
            ]
        ])
    )
    

    def __init__(self, **kwargs) -> None:
        self.__fields = {}
        for k, v in kwargs.items():
            self.__fields[k.lower()] = v
        
        self.logger = get_logger("HDR")

    def __getitem__(self, key) -> str:
        key = key.lower()
        if key not in self.REPEATABLE_HEADERS:
            return self.__fields.get(key, "")
        else:
            raise ValueError(f"Use get_all() to get all values of header '{key}'")
    
    def __setitem__(self, key, value):
        key = key.lower()
        values = self.__fields.get(key, None)
        if isinstance(values, list):
            raise ValueError(f"Use add() to add value to header '{key}' or use set() to replace all values")
        self.__fields[key.lower()] = value
        
    def __delitem__(self, key):
        del self.__fields[key.lower()]

    def get_all(self, key) -> list:
        key = key.lower()
        if key in self.REPEATABLE_HEADERS:
            return self.__fields.get(key, [])
        else:
            return [self.__fields.get(key, "")]

    def add(self, key, value):
        key = key.lower()
        values = self.__fields.get(key, None)
        if values is None:
            self.__fields[key] = value
        elif isinstance(values, list):
            values.append(value)
        else:
            self.__fields[key] = [values, value]

    def set(self, key, value):
        self.__fields[key.lower()] = value
        
    def __contains__(self, key):
        return key.lower() in self.__fields
    
    def __len__(self):
        """
        Return the number of headers. Repeatable headers are counted as the number of values.
        """
        return sum([len(v) if isinstance(v, list) else 1 for v in self.__fields.values()])
    
    def __iter__(self):
        """
        Iterate through all headers and their values. Repeatable headers are yielded multiple times.
        """
        for key, value in self.__fields.items():
            if isinstance(value, list):
                for v in value:
                    yield (key, v)
            else:
                yield (key, value)

    def items(self):
        """
        Return a list of (key, value) pairs. Repeatable headers are yielded multiple times.
        """
        return list(self)

    def clear(self):
        self.__fields.clear()

    def parse(self, sock: socket.socket):
        self.__fields.clear()
        while True:
            line = readline(sock)
            if line == '':
                break
            key, value = line.split(':', 1)
            self.add(key, value.strip())
    
    def send(self, sock: socket.socket):
        buf = io.BytesIO()
        self.write(buf)
        sock.sendall(buf.getvalue())
    
    def write(self, file: io.BytesIO):
        for key, value in self:
            file.write(f"{key}: {value}\r\n".encode())
      
    def copy(self) -> 'Headers':
        return Headers(**deepcopy(self.__fields))

    def log(self, logger, level=logging.DEBUG, prefix=""):
        for k, v in self:
            logger.log(level, f"{prefix}{k}: {v}")


class HTTPRequest:
    def __init__(self, method="GET", uri="/", protocol="HTTP/1.1") -> None:
        self.method = method.upper()
        self.uri = uri
        self.protocol = protocol
        self.headers = Headers()
        
        self.logger = get_logger("REQ")
        
    def parse(self, sock: socket):
        request_line = readline(sock)
        method, uri, protocol = request_line.split(" ")
        self.method = method
        self.uri = uri
        self.protocol = protocol
        
        self.headers.parse(sock)
    
    def send(self, sock: socket):
        buf = io.BytesIO()
        self.write(buf)
        sock.sendall(buf.getvalue())
    
    def write(self, file: io.BytesIO):
        file.write(f"{self.method} {self.uri} {self.protocol}\r\n".encode())
        self.headers.write(file)
        file.write(b"\r\n")

    def copy(self):
        req = HTTPRequest(self.method, self.uri, self.protocol)
        req.headers = self.headers.copy()
        return req
    
    def has_body(self):
        return self.method in ["POST", "PUT", "PATCH"]

class HTTPResponse:
    def __init__(self, protocol="HTTP/1.1", status_code=200, status="OK") -> None:
        self.protocol = protocol
        self.status_code = status_code
        self.status = status
        self.headers = Headers()
        
        self.logger = get_logger("RES")
    
    def parse(self, sock: socket.socket):
        response_line = readline(sock)
        self.logger.debug(f"parse response line: {response_line}")
        tokens = response_line.split(" ")
        if len(tokens) == 2:
            protocol, status_code = tokens
            status = ""
        elif len(tokens) >= 3:
            protocol = tokens[0]
            status_code = tokens[1]
            status = " ".join(tokens[2:])
        else:
            raise Exception(f"Invalid response line: '{response_line}'")
        self.protocol = protocol
        self.status_code = int(status_code)
        self.status = status
        
        self.headers.parse(sock)
    
    def send(self, sock: socket.socket):
        """send response and headers to socket
        """
        buf = io.BytesIO()
        self.write(buf)
        sock.sendall(buf.getvalue())
    
    def write(self, file: io.BytesIO):
        file.write(f"{self.protocol} {self.status_code} {self.status}\r\n".encode())
        self.headers.write(file)
        file.write(b"\r\n")
    
    def copy(self):
        res = HTTPResponse(self.protocol, self.status_code, self.status)
        res.headers = self.headers.copy()
        return res
        
    
    @staticmethod
    def method_not_allowed():
        res = HTTPResponse()
        res.status_code = 405
        res.status = "Method Not Allowed"
        return res

    
    @staticmethod
    def bad_request():
        res = HTTPResponse()
        res.status_code = 400
        res.status = "Bad Request"
        return res


class HTTPBody:
    def __init__(self, headers: Headers, sock: socket.socket) -> None:
        self.headers = headers
        self.sock = sock
        self.bufsz = 4096
        
        self.logger = get_logger("BODY")
        
    def itr_data(self) -> Iterable[bytes]:
        if "Content-Length" in self.headers:
            yield from self.read_fixed_length()
        elif "chunked" in self.headers["Transfer-Encoding"]:
            yield from self.read_chunked()
        elif "close" in self.headers["Connection"].lower():
            yield from self.read_until_close()
        else:
            logger = self.logger
            logger.error(f"Unsupported transfer encoding, headers: ")
            for k, v in self.headers:
                logger.error(f"  {k}: {v}")
            
            raise Exception("Unsupported transfer encoding")
    
    def read_until_close(self) -> Iterable[bytes]:
        self.logger.debug(f"read_until_close")
        while True:
            data = self.sock.recv(self.bufsz)
            if not data: break
            yield data

    def read_fixed_length(self) -> Iterable[bytes]:
        self.logger.debug(f"read_fixed_length")
        content_length = int(self.headers['Content-Length'])
        cur_sz = 0
        while cur_sz < content_length:
            data = self.sock.recv(min(self.bufsz, content_length - cur_sz))
            if not data: break
            cur_sz += len(data)
            
            self.logger.debug(f"read_fixed_length: {cur_sz}/{content_length}")
            yield data
    
    def read_chunked(self) -> Iterable[bytes]:
        self.logger.debug(f"read_chunked")
        while True:
            line = readline(self.sock)
            chunk_size = int(line, 16)
            self.logger.debug(f"read_chunked: new chunk, size={chunk_size}")
            if chunk_size == 0:
                self.logger.debug(f"read_chunked: end of chunks")
                readline(self.sock)
                break
            cur_sz = 0
            while cur_sz < chunk_size:
                data = self.sock.recv(min(self.bufsz, chunk_size - cur_sz))
                if not data: break
                cur_sz += len(data)
                yield data
            self.logger.debug(f"read_chunked: read {cur_sz}/{chunk_size}")
            readline(self.sock)
    
    def chunked(self) -> bool:
        return "chunked" in self.headers["Transfer-Encoding"].lower()

class HTTPHandler:
    def __init__(self, client_sock: socket.socket) -> None:
        self.client_sock = client_sock
    
    def handle(self):
        pass

class HTTPServer:
    def __init__(self, hdl_class: HTTPHandler.__class__, listen=("127.0.0.1", 8443), hdl_extra = {}) -> None:
        self.listen_addr = listen
        self.listen_sock = socket.create_server(self.listen_addr)
        self.hdl_class = hdl_class
        self.hdl_extra = hdl_extra
        
        self.serving = False
        
        self.logger = get_logger("SVR")
        
        
    def serve_forever(self):
        self.logger.info(f"Start serving on {self.listen_addr}")
        
        self.serving = True
        while self.serving:
            sock, addr = self.listen_sock.accept()
            self.logger.info(f"Accept connection from {addr}")
            
            threading.Thread(target=self.handle_wrapper, args=(sock, )).start()
    
    def handle_wrapper(self, sock: socket.socket):
        try:
            handler = self.hdl_class(sock, **self.hdl_extra)
            handler.handle()
        except Exception as e:
            self.logger.exception(f"Exception in handler: {e}")
            sock.close()


class EchoHandler(HTTPHandler):
    def __init__(self, client_sock: socket.socket) -> None:
        super().__init__(client_sock)
        self.logger = get_logger("ECHO")
    
    def handle(self):
        client_sock = self.client_sock
        logger = self.logger
        
        keep_alive = True
        
        while keep_alive:
            req = HTTPRequest()
            req.parse(self.client_sock)
            
            logger.debug(f"Request: {req.method} {req.uri} {req.protocol}")
            logger.debug(f"Headers: ")
            for k, v in req.headers:
                logger.debug(f"  {k}: {v}")
        
            logger.debug(f"ECHO: send HTTP response")    
            res = HTTPResponse()
            res.protocol = "HTTP/1.1"
            res.status_code = 200
            res.status = "OK"
            res.headers = req.headers.copy()
            res.headers["Content-Type"] = "text/plain"
            res.headers["Content-Length"] = 0
            res.headers["Transfer-Encoding"] = "chunked"
            if req.headers["Connection"].lower() == "close":
                res.headers["Connection"] = "close"
                keep_alive = False
            elif req.headers["Connection"].lower() == "keep-alive":
                res.headers["Connection"] = "keep-alive"
                keep_alive = True
            else:
                res.headers["Connection"] = "close"
                keep_alive = False
            
            res.send(client_sock)

            # echo request headers
            logger.debug(f"ECHO: send request headers")
            buf = io.BytesIO()
            req.write(buf)
            send_chunk(client_sock, buf.getvalue())
            
            # echo request body if necessary
            if req.method in ["POST", "PUT", "PATCH"]:
                logger.debug(f"ECHO: sending request body")
                for data in HTTPBody(req.headers, client_sock).itr_data():
                    logger.debug(f"ECHO: sending segment: {data}")
                    send_chunk(client_sock, data)
                    
            send_chunk(client_sock, b"")
            logger.debug(f"ECHO: done")
            
        self.client_sock.close()
