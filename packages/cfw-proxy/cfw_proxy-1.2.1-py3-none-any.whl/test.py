from cfw_proxy2 import http_conn as H
from cfw_proxy2.http_client import HttpClient
from icecream import ic
import socket

def simple_request():
    s1, s2 = socket.socketpair()
    client = HttpClient("echo.crychic.uk", https=True)

    # first request
    ic("First request")
    req = H.HTTPRequest("POST", "/")
    req.headers.set("Host", "echo.crychic.uk")

    data = "hello from client".encode()
    req.headers.set("Content-Length", len(data))
    s1.send(data)
    req.reset_body(s2)


    ic(req.headers)
    with client.send_request(req) as resp:
        ic(resp.status_code)
        ic(resp.headers)
        resp.read_body()
        # ic(resp.read_body())
    ic(client.sock)

    # second request
    ic("second request")
    req = H.HTTPRequest("GET", "/")
    req.headers.set("Host", "echo.crychic.uk")
    req.headers.set("Connection", "close")

    with client.send_request(req) as resp:
        ic(resp.status_code)
        ic(resp.headers)
        resp.read_body()
        # ic(resp.read_body())
    ic(client.sock)

if __name__ == "__main__":
    simple_request()