"""
HTTPproxy.py
============
A basic HTTP/1.0 forwarding proxy.

Scope: GET only, absolute URI request lines, single request per connection.
Caching, filtering, blocklists, and HTTPS are out of scope.

Usage:
    python3.10 HTTPproxy.py [-a INTERFACE] [-p PORT]

Defaults: listen on localhost:2100.
"""

import argparse
import socket
import sys


# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

RECV_CHUNK = 8192
SMALL_BUFFER = 4096
LISTEN_BACKLOG = 100
CLIENT_TIMEOUT = 30
ORIGIN_TIMEOUT = 30


# ----------------------------------------------------------------------------
# HTTP parsing / response helpers
# ----------------------------------------------------------------------------

def send_error(client_sock, code, phrase):
    """Send a minimal HTTP/1.0 error response to the client and close."""
    body = f"{code} {phrase}".encode("ascii")
    response = (
        f"HTTP/1.0 {code} {phrase}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"
    ).encode("ascii") + body
    try:
        client_sock.sendall(response)
    except OSError:
        pass


def recv_until_end_of_headers(sock):
    """
    Read the client's request from `sock`.

    Returns the raw bytes read, or None if the connection closed early or the
    request grew past the size cap.
    """
    buf = b""
    while b"\r\n" not in buf:
        chunk = sock.recv(RECV_CHUNK)
        if not chunk:
            return None
        buf += chunk
        if len(buf) > 65536:
            return None
    return buf


def parse_request(raw):
    """
    Parse an HTTP/1.0 request into method / url / version / headers.

    Returns a dict with keys method, url, version, headers, or None if the
    request is malformed.
    """
    try:
        text = raw.decode("iso-8859-1")
    except UnicodeDecodeError:
        return None

    head, _, _ = text.partition("\r\n\r\n")
    lines = head.split("\r\n")
    if not lines:
        return None

    request_line = lines[0]
    parts = request_line.split(" ")
    if len(parts) != 3:
        return None
    method, url, version = parts

    headers = {} #! Flag 4
    for line in lines[1:]:
        if not line:
            continue

        if ":" not in line:
            return None
        
        name, _, value = line.partition(": ") #! Flag 2

        if ' ' in name:
            return None
        
        if not name:
            return None
        
        headers[name] = value #! Flag 4

    return {
        "method": method,
        "url": url,
        "version": version,
        "headers": headers,
    }


def parse_absolute_url(url):
    """Parse http://host[:port]/path into (host, port, path) or return None."""
    if not url.startswith("http://"):
        return None
    rest = url[len("http://"):]

    slash = rest.find("/")
    if slash < 0:
        return None
    hostport = rest[:slash]
    path = rest[slash:]

    if not hostport:
        return None

    if ":" in hostport:
        host, _, port_str = hostport.partition(":")
        if not host or not port_str.isdigit():
            return None
        port = int(port_str)
    else:
        host = hostport
        port = 80

    return host, port, path


# ----------------------------------------------------------------------------
# Request forwarding
# ----------------------------------------------------------------------------

def build_forwarded_request(method, url, path, host, headers):
    """
    Build the request to send to the origin server.

    Returns the encoded request bytes, terminated by the end of headers
    marker.
    """
    lines = [f"{method} {path} HTTP/1.0"] #! Flag 3

    for name, value in headers.items(): #! Flag 4
        lines.append(f"{name}: {value}")

    return ("\r\n".join(lines) + "\r\n\r\n").encode("iso-8859-1")


def forward_and_stream_response(client_sock, host, port, forwarded_request):
    """
    Forward the request to the origin and return the response to the client.
    """
    origin_sock = None
    try:
        origin_sock = socket.create_connection((host, port), timeout=ORIGIN_TIMEOUT)
        origin_sock.sendall(forwarded_request)

        chunk = origin_sock.recv(SMALL_BUFFER)
        if chunk:
            client_sock.sendall(chunk)

    except (socket.gaierror, ConnectionRefusedError, socket.timeout, OSError):
        send_error(client_sock, 502, "Bad Gateway")
    finally:
        if origin_sock is not None:
            try:
                origin_sock.close()
            except OSError:
                pass


# ----------------------------------------------------------------------------
# Per-client handler
# ----------------------------------------------------------------------------

def handle_client(client_sock, client_addr):
    """
    Handle one client connection end to end.
    """
    try:
        client_sock.settimeout(CLIENT_TIMEOUT)

        raw = recv_until_end_of_headers(client_sock)
        if raw is None:
            send_error(client_sock, 400, "Bad Request")
            return

        parsed = parse_request(raw)
        if parsed is None:
            send_error(client_sock, 400, "Bad Request")
            return

        if parsed['version'] != 'HTTP/1.0':  #! Flag 1
            send_error(client_sock, 400, "Bad Request")
            return

        if parsed["method"] != "GET":
            send_error(client_sock, 501, "Not Implemented")
            return

        parsed_url = parse_absolute_url(parsed["url"])
        if parsed_url is None:
            send_error(client_sock, 400, "Bad Request")
            return
        host, port, path = parsed_url

        if 'Host' not in parsed["headers"]: #! Flag 4
            parsed["headers"]['Host'] = 'localhost'

        if ('Connection', 'close') not in parsed["headers"].items():  #! Flag 5
            parsed["headers"]['Connection'] = 'close'

        forwarded = build_forwarded_request(
            parsed["method"], parsed["url"], path, host, parsed["headers"]
        )

        forward_and_stream_response(client_sock, host, port, forwarded)

    except socket.timeout:
        send_error(client_sock, 408, "Request Timeout")
    except Exception:
        try:
            send_error(client_sock, 500, "Internal Server Error")
        except Exception:
            pass
    finally:
        try:
            client_sock.close()
        except OSError:
            pass


# ----------------------------------------------------------------------------
# Server entry point
# ----------------------------------------------------------------------------

def serve(interface, port):
    """
    Accept connections and handle them.
    """
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((interface, port))
    listen_sock.listen(LISTEN_BACKLOG)

    try:
        while True:
            client_sock, client_addr = listen_sock.accept()
            handle_client(client_sock, client_addr)
    except KeyboardInterrupt:
        pass
    finally:
        listen_sock.close()


def main():
    parser = argparse.ArgumentParser(description="HTTP/1.0 proxy.")
    parser.add_argument("-a", dest="interface", default="localhost",
                        help="Interface to bind (default: localhost)")
    parser.add_argument("-p", dest="port", type=int, default=2100,
                        help="Port to listen on (default: 2100)")
    args = parser.parse_args()
    serve(args.interface, args.port)


if __name__ == "__main__":
    main()
