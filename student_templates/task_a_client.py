"""
Task A: Simple TCP client.

Fill in the function `fetch(host, port, message)`.  It must:

  1. Open a TCP socket
  2. Connect to (host, port)
  3. Send `message` (already bytes) using sendall()
  4. Half-close the send side so the server knows you're done sending
     (see the M0 handout, Task A section, for why this is needed)
  5. Read all bytes from the server until it closes the connection
  6. Close the socket
  7. Return the received bytes

Do NOT print anything.  Do NOT modify anything outside the TODO region.
Our test harness imports `fetch` from this file and checks the return value.

Objectives exercised: 1, 3, 7  (see M0 handout for objective numbers)
"""

import socket


def fetch(host: str, port: int, message: bytes) -> bytes:
    """
    Send `message` to a TCP server at (host, port) and return everything the
    server sends back.

    Parameters:
        host    - hostname or IP address to connect to
        port    - TCP port to connect to
        message - bytes to send to the server

    Returns:
        bytes received from the server (may be empty if the server sent nothing)
    """
    # ---- TODO: implement below this line ----

    raise NotImplementedError("Task A: implement fetch()")

    # ---- TODO: implement above this line ----


if __name__ == "__main__":
    # Optional: you can add your own smoke test here.  This block is ignored
    # by the autograder.
    pass
