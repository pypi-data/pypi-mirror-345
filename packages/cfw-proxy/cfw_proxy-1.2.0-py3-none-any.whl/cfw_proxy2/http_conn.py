import socket
import io
from typing import Iterable
import ssl
from copy import deepcopy
from typing import Union
import time

ConnType = Union[socket.socket, ssl.SSLSocket]


class HTTPConnErr(Exception):
    pass


class ConnClosed(HTTPConnErr):
    pass


class ParseError(HTTPConnErr):
    pass


class InvalidBody(HTTPConnErr):
    pass


class BodyConsumed(HTTPConnErr):
    pass


def patch_ssl_socket(ssl_sock: ssl.SSLSocket):
    original_recv = ssl_sock.recv
    buffer = io.BytesIO()

    def peekable_recv(self, bufsize, flags=0):
        nonlocal original_recv
        nonlocal buffer

        if flags not in (0, socket.MSG_PEEK):
            raise ValueError("Invalid flags, only 0 and MSG_PEEK are allowed")

        # Peek
        if flags == socket.MSG_PEEK:
            # Fill the buffer until bufsize is reached
            buffer.seek(0, io.SEEK_END)
            if buffer.tell() == 0:
                chunk = original_recv(bufsize)
                buffer.write(chunk)

            buffer.seek(0)
            data = buffer.read(bufsize)
            buffer.seek(0)
            return data

        # Normal recv
        buffer.seek(0, io.SEEK_END)
        if buffer.tell() > 0:
            buffer.seek(0)
            data = buffer.read(bufsize)
            buffer = io.BytesIO(buffer.read())
        else:
            data = original_recv(bufsize)
        return data

    ssl_sock.recv = peekable_recv.__get__(ssl_sock, ssl.SSLSocket)
    return ssl_sock


def readline(sock: ConnType) -> str:
    """
    Read one line from the socket.

    Github may response headers with extremely long values, so this function
    should be robust.

    Exceptions:
        - ConnClosed: if the connection is closed
        - ParseError: line too long
    """

    bufsz = 4096
    data = b""
    idx = -1

    timeout = sock.gettimeout()
    start_time = time.monotonic()
    while idx == -1:
        cur_time = time.monotonic()
        if timeout is not None and cur_time - start_time > timeout:
            raise ParseError("line too long, timeout")

        chunk = sock.recv(bufsz, socket.MSG_PEEK)
        if not chunk:
            raise ConnClosed()

        idx = chunk.find(b"\n")
        if idx != -1:
            sock.recv(idx + 1)
            data += chunk[: idx + 1]
            break
        elif len(data) <= bufsz:
            sock.recv(len(chunk))
            data += chunk
        else:
            raise ParseError("line too long, buffer size exceeded")

    line = data.decode()
    line = line.rstrip("\r\n")
    return line


def send_chunk(sock: ConnType, data: bytes):
    """
    Send a chunk of data according to the HTTP/1.1 chunked transfer encoding.

    First, the length of the data is sent in hexadecimal, followed by a CRLF.
    Then, the data is sent, followed by a CRLF.

    The format specification is available at
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding.
    """

    sock.sendall(f"{hex(len(data))[2:]}\r\n".encode())
    sock.sendall(data)
    sock.sendall(b"\r\n")


def get_peer_addr(sock: ConnType) -> str:
    """
    Address format "ip:port"
    """
    peername = sock.getpeername()
    return f"{peername[0]}:{peername[1]}"


class Headers:
    def __init__(self):
        self._fields = {}

    def get(self, field: str) -> str | list[str] | None:
        """
        Get a header field. If the field does not exist, return None.
        """
        field = field.lower()
        return self._fields.get(field)

    def set(self, field: str, value: str | list[str]):
        """
        Set a header entry regardless of whether it already exists.
        """
        field = field.lower()
        self._fields[field] = value

    def add(self, field: str, value):
        """
        Add a value to a header field.

        If the field does not exist, it is created. If the field already exists,
        it is converted to the repeated header automatically, and the new value
        is appended to the list.

        Take care about the difference between "list-based headers" and
        "repeated headers". List-based headers have comma-separated values in a
        single line, such as `Accept-Encoding: gzip, deflate`. Repeated headers
        have multiple lines of the same header field.

        For example,
        ```
        headers = Headers()
        headers.add("Set-Cookie", "a=b")
        headers.add("Set-Cookie", "c=d")
        ```
        Then the headers will contain 2 lines of "Set-Cookie".
        """
        field = field.lower()
        current_value = self._fields.get(field)
        if current_value is None:
            self._fields[field] = value
        elif isinstance(current_value, list):
            current_value.append(value)
        else:
            self._fields[field] = [current_value, value]

    def __contains__(self, field: str):
        return field.lower() in self._fields

    def keys(self):
        return self._fields.keys()

    def remove(self, field: str):
        field = field.lower()
        if field in self._fields:
            del self._fields[field]

    def clear(self):
        self._fields.clear()

    @staticmethod
    def parse(sock: ConnType) -> "Headers":
        """
        Parse headers from a socket.

        Exceptions:
            - ConnClosed: if the connection is closed
            - TimeoutError: No data is read within the timeout. The caller
              should try later.
            - ParseError:
                - Header reading started but not finished within timeout
                - Line too long
        """
        headers = Headers()
        time_of_first_line = None
        while True:
            try:
                line = readline(sock)
            except TimeoutError:
                if time_of_first_line is not None:
                    raise ParseError(
                        "Header reading started but not finished within timeout"
                    )
                else:
                    raise  # No header is read, pass the TimeoutError to the caller

            if time_of_first_line is None:
                time_of_first_line = time.monotonic()
            else:
                cur_time = time.monotonic()
                if cur_time - time_of_first_line > sock.gettimeout():
                    raise ParseError(
                        "Header reading started but not finished within timeout"
                    )

            if line == "":
                break
            key, value = line.split(":", 1)
            headers.add(key, value.strip())
        return headers

    def __repr__(self):
        return repr(self._fields)

    def send(self, sock: ConnType):
        for key, value in self._fields.items():
            if isinstance(value, list):
                for v in value:
                    sock.sendall(f"{key}: {v}\r\n".encode())
            else:
                sock.sendall(f"{key}: {value}\r\n".encode())

    def copy(self) -> "Headers":
        new_headers = Headers()
        new_headers._fields = deepcopy(self._fields)
        return new_headers


class HTTPBody:
    def __init__(self, headers: Headers, sock: ConnType, bufsz: int = 4096):
        self.headers = headers
        self.sock = sock
        self.bufsz = bufsz

        if sock is None:
            # The body is empty, Content-Length should be 0.
            if headers.get("Content-Length") != "0":
                raise InvalidBody(
                    "Content-Length should be 0 for an empty body stream."
                )

    def iterator(self) -> Iterable[bytes]:
        if "Content-Length" in self.headers:
            yield from self._read_fixed_length()
        elif "chunked" in self.headers.get("Transfer-Encoding"):
            yield from self._read_chunked()
        elif "close" in self.headers.get("Connection").lower():
            yield from self._read_until_close()
        else:
            raise InvalidBody(
                "Invalid HTTP body. At least one of Content-Length, "
                + "Transfer-Encoding, or `Connection: close` must be specified."
            )

    def _read_until_close(self) -> Iterable[bytes]:
        """
        Used when no Content-Length or Transfer-Encoding is specified.
        """
        while True:
            data = self.sock.recv(self.bufsz)
            if not data:
                break
            yield data

    def _read_fixed_length(self) -> Iterable[bytes]:
        """
        Used when Content-Length is specified.
        """

        content_length = int(self.headers.get("Content-Length"))
        cur_sz = 0
        while cur_sz < content_length:
            data = self.sock.recv(min(self.bufsz, content_length - cur_sz))
            if not data:
                break
            cur_sz += len(data)
            yield data

    def _read_chunked(self) -> Iterable[bytes]:
        while True:
            line = readline(self.sock)
            chunk_size = int(line, 16)
            if chunk_size == 0:  # end of body
                readline(self.sock)
                break

            cur_sz = 0
            while cur_sz < chunk_size:
                data = self.sock.recv(min(self.bufsz, chunk_size - cur_sz))
                if not data:
                    break
                cur_sz += len(data)
                yield data
            readline(self.sock)

    def send(self, sock: ConnType):
        chunked = "chunked" in (self.headers.get("Transfer-Encoding") or "")
        if chunked:
            for chunk in self.iterator():
                send_chunk(sock, chunk)
            send_chunk(sock, b"")
        else:
            for chunk in self.iterator():
                sock.sendall(chunk)


class HTTPRequest:
    MTH_MAY_HAVE_BODY = ["DELETE", "POST", "PUT", "PATCH"]

    def __init__(self, method: str = "GET", uri: str = "/", protocol: str = "HTTP/1.1"):
        self.method = method.upper()
        self.uri = uri
        self.protocol = protocol
        self.headers = Headers()
        self._body_stream = None
        self._body_consumed = False

    def reset_body(self, body_stream: socket.socket):
        """
        Reset the body stream to a new socket.

        If the stream is expected to be read from a IO stream rather than a
        socket, consider using `socket.socketpair`.
        """

        self._body_stream = body_stream
        self._body_consumed = False

    def may_have_body(self):
        return self.method in HTTPRequest.MTH_MAY_HAVE_BODY

    @staticmethod
    def parse(sock: ConnType):
        request_line = readline(sock)
        mth, uri, proto = request_line.split(" ")
        req = HTTPRequest(mth, uri, proto)
        req.headers = Headers.parse(sock)
        req._body_stream = sock
        return req

    def send(self, sock: ConnType):
        if self._body_consumed:
            raise BodyConsumed()

        sock.sendall(f"{self.method} {self.uri} {self.protocol}\r\n".encode())
        self.headers.send(sock)
        sock.sendall(b"\r\n")

        if self.may_have_body() and self._body_stream is not None:
            body = HTTPBody(self.headers, self._body_stream)
            body.send(sock)


class HTTPResponse:
    STATUS_CODES_WITHOUT_BODY = (100, 101, 102, 103, 204, 205, 304)

    def __init__(
        self,
        protocol: str = "HTTP/1.1",
        status_code: int = 200,
        reason: str = "OK",
        related_request: HTTPRequest | None = None,
    ):
        self.protocol = protocol
        self.status_code = status_code
        self.reason = reason
        self.headers = Headers()
        self.related_request = related_request
        self._body_stream = None
        self._body_consumed = False

    @staticmethod
    def parse(sock: ConnType):
        status_line = readline(sock)
        tokens = status_line.split(" ")
        if len(tokens) == 2:
            protocol, status_code = tokens
            reason = ""
        elif len(tokens) >= 3:
            protocol = tokens[0]
            status_code = tokens[1]
            reason = " ".join(tokens[2:])
        else:
            raise ParseError(f"Invalid status line: `{status_line}`")

        resp = HTTPResponse(protocol, int(status_code), reason)
        resp.headers = Headers.parse(sock)
        resp._body_stream = sock
        return resp

    def send(self, sock: ConnType):
        if self._body_consumed:
            raise BodyConsumed()

        if self.related_request is None:
            raise ValueError("self.related_request is None, and is required by `send`")

        sock.sendall(f"{self.protocol} {self.status_code} {self.reason}\r\n".encode())
        self.headers.send(sock)
        sock.sendall(b"\r\n")

        if self.related_request.method == "HEAD":
            return

        if self.status_code not in HTTPResponse.STATUS_CODES_WITHOUT_BODY:
            self._body_consumed = True
            body = HTTPBody(self.headers, self._body_stream)
            body.send(sock)

    def reset_body(self, body_stream: socket.socket):
        self._body_stream = body_stream
        self._body_consumed = False

    def read_body(self) -> bytes:
        if self._body_consumed:
            raise BodyConsumed()

        if self.status_code in HTTPResponse.STATUS_CODES_WITHOUT_BODY:
            return b""

        self._body_consumed = True
        body = HTTPBody(self.headers, self._body_stream)
        data = b"".join(body.iterator())
        return data

    def iter_body(self) -> Iterable[bytes]:
        if self._body_consumed:
            raise BodyConsumed()

        if self.status_code in HTTPResponse.STATUS_CODES_WITHOUT_BODY:
            yield b""

        self._body_consumed = True
        body = HTTPBody(self.headers, self._body_stream)
        yield from body.iterator()

    class PseudoRelatedRequest:
        def __init__(self):
            self.method = "GET"

    @staticmethod
    def bad_request():
        resp = HTTPResponse()
        resp.status_code = 400
        resp.reason = "Bad Request"
        resp.headers.set("Content-Length", "0")
        resp.related_request = HTTPResponse.PseudoRelatedRequest()
        return resp

    @staticmethod
    def service_unavailable():
        resp = HTTPResponse("HTTP/1.1", 503, "Service Unavailable")
        resp.headers.set("Connection", "close")
        resp.headers.set("Retry-After", "10")
        resp.headers.set("Content-Length", "0")
        resp.related_request = HTTPResponse.PseudoRelatedRequest()
        return resp

    @staticmethod
    def method_not_allowed(allowed_methods: Iterable[str]):
        resp = HTTPResponse("HTTP/1.1", 405, "Method Not Allowed")
        resp.headers.set("Connection", "close")
        resp.headers.set("Allow", ", ".join(allowed_methods))
        resp.headers.set("Content-Length", "0")
        resp.related_request = HTTPResponse.PseudoRelatedRequest()
        return resp
