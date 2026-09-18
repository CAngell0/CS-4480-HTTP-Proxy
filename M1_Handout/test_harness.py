"""
test_harness.py - helper utilities for PA1 Milestone 1.

Provided to students so they don't have to re-implement a small HTTP server
in every test.  Import from this file in your tests.py:

    from test_harness import MockOrigin

You are welcome to read this file to understand what it does, but do not
modify it in your submission - the autograder uses its own copy.
"""

import socket
import threading
import time


class MockOrigin:
    """
    A tiny HTTP server that captures whatever the proxy forwards to it.

    Typical use:

        origin = MockOrigin(port=19000)
        try:
            # ... send a request through the proxy targeting localhost:19000 ...
            received_bytes = origin.received
            # ... assertions about received_bytes ...
        finally:
            origin.close()

    Parameters:
        port      - TCP port to listen on (must be free; pick per-test)
        body_size - number of bytes to send in the canned response body
        body_char - the byte to repeat in the body (default b'.')

    Attributes populated after a request comes in:
        received  - the raw bytes the origin received from the proxy, up to
                    and including the \\r\\n\\r\\n end-of-headers marker.
                    None if no request has arrived yet.
    """

    def __init__(self, port, body_size=16, body_char=b"."):
        self.port = port
        self.body_size = body_size
        self.body_char = body_char
        self.received = None

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("localhost", port))
        self._sock.listen(4)
        self._sock.settimeout(0.5)

        self._stop = False
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        while not self._stop:
            try:
                conn, _ = self._sock.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                conn.settimeout(3.0)
                buf = b""
                while b"\r\n\r\n" not in buf:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                    if len(buf) > 65536:
                        break
                # Only overwrite `received` on the first connection so a
                # single test isn't confused by follow-on traffic.
                if self.received is None:
                    self.received = buf

                body = self.body_char * self.body_size
                response = (
                    b"HTTP/1.0 200 OK\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: " + str(len(body)).encode() + b"\r\n"
                    b"Connection: close\r\n"
                    b"\r\n" + body
                )
                conn.sendall(response)
            except OSError:
                pass
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    def close(self):
        """Shut down the mock origin.  Safe to call multiple times."""
        self._stop = True
        try:
            self._sock.close()
        except OSError:
            pass
        # Give the accept loop a moment to notice the socket is closed.
        time.sleep(0.05)
