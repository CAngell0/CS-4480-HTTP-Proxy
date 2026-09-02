"""
Task C: recv_exactly.

Fill in the function `recv_exactly(sock, n)`.  It must read exactly `n` bytes
from `sock` and return them, or return None if the peer closes the connection
before `n` bytes arrive.

Why this task exists:
    In Objective 3 of the M0 handout, you read that TCP is a byte stream, not
    a message stream.  A single call to sock.recv(n) may return fewer than
    n bytes even if the sender sent more.  If you're expecting a fixed
    number of bytes (for example, the 4-byte length prefix of a
    length-prefixed protocol), you MUST loop until you have them all.

    This task isolates that pattern.  The rest of the length-prefixed
    protocol logic is provided for you by our test harness.

Requirements:
    - Return exactly n bytes if the peer sends at least n before closing
    - Return None if the peer closes before n bytes arrive
    - Do NOT call recv() with a buffer size larger than what you still need
      (this is not enforced, but it's good practice - otherwise you might
      consume bytes belonging to the next message)
    - Do NOT modify anything outside the TODO region

Objectives exercised: 1, 3, 5, 6  (primarily objectives 3 and 6)
"""

import socket


def recv_exactly(sock: socket.socket, n: int) -> bytes | None:
    """
    Read exactly `n` bytes from `sock`, blocking until they arrive.

    Parameters:
        sock - a connected TCP socket
        n    - number of bytes to read (n >= 0)

    Returns:
        The n bytes as a `bytes` object, OR
        None if the peer closed the connection before n bytes arrived.
    """
    # ---- TODO: implement below this line ----

    raise NotImplementedError("Task C: implement recv_exactly()")

    # ---- TODO: implement above this line ----


if __name__ == "__main__":
    pass
