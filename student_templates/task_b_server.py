"""
Task B: Simple TCP server.

Fill in the function `serve_one(port)`.  It must:

  1. Open a TCP listening socket
  2. Set SO_REUSEADDR on it (see the M0 handout, Concept 6)
  3. Bind to ('localhost', port)
  4. Listen for connections
  5. Accept exactly ONE client connection
  6. Read all bytes from that client until the client closes their send side
  7. Send back the received bytes prefixed with b"REPLY: "
  8. Close the client socket
  9. Close the listening socket
 10. Return the bytes that were received from the client (before prefixing)

The function should return after handling exactly one connection.  Do NOT
loop; do NOT run forever.  Our test harness calls serve_one() in a background
thread and then connects as the client.

Objectives exercised: 1, 2, 3, 5, 6, 7  (see M0 handout for objective numbers)
"""

import socket


def serve_one(port: int) -> bytes:
    """
    Accept one connection on `port`, echo the client's message back with the
    "REPLY: " prefix, then close.

    Parameters:
        port - TCP port to listen on

    Returns:
        the bytes the client sent (without the "REPLY: " prefix)
    """
    # ---- TODO: implement below this line ----

    raise NotImplementedError("Task B: implement serve_one()")

    # ---- TODO: implement above this line ----


if __name__ == "__main__":
    pass
