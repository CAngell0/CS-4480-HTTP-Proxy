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

    # Constant used for the safe read amount so as to not read bytes from the next message
    SAFE_READ_AMOUNT = 2048
    # Keeps track of how many bytes are left to be read
    remaining_bytes = n
    # Holds the data that has been collected so far
    recieved = b''

    # While there is still bytes to read...
    while remaining_bytes != 0:
        data_chunk = b''

        # If the remaining bytes to read are more than the amount I can safely read. Read a chunk 
        # of bytes at an amount that is safe
        if remaining_bytes >= SAFE_READ_AMOUNT:
            data_chunk = sock.recv(SAFE_READ_AMOUNT)
            remaining_bytes -= SAFE_READ_AMOUNT
        # Otherwise, just read the chunk of data that's left after the safe reads.
        else:
            data_chunk = sock.recv(remaining_bytes)
            remaining_bytes = 0

        # If the data flow ended before all the bytes have been read, break
        if not data_chunk: break;
        else: recieved += data_chunk

    if len(recieved) < n: return None
    else: return recieved


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8888))
    sock.sendall(b'Hello World!')
    sock.shutdown(socket.SHUT_WR)

    data = recv_exactly(sock, 100)
    print("None" if data is None else data.decode())

    pass
