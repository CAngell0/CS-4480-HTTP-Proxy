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

    # Create the TCP socket and make the connection to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Send the message to the server
    client_socket.sendall(message)

    # Tell the server that I am done sending data ("half-close")
    client_socket.shutdown(socket.SHUT_WR)

    # Read all the data the server sends until its done
    response = b''
    while True:
        data_chunk = client_socket.recv(2048)
        if not data_chunk: break

        response += data_chunk

    # Close the connection and return the response.
    client_socket.close()
    return response


if __name__ == "__main__":
    # Optional: you can add your own smoke test here.  This block is ignored
    # by the autograder.
    print(
        fetch('localhost', 8888, b'Hello World!').decode()
    )
    pass
