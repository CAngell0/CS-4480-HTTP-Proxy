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

    # Create the socket (with socket socket reuse enabled, TCP and correc binding)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', port))

    # Start listening for connections
    server_socket.listen()

    # Accept exactly one client and move forward
    client, _ = server_socket.accept()


    # Read all packets until the client is done sending and put them in the 'recieved' variable
    recieved = b''
    while True:
        data_chunk = client.recv(2048)
        if not data_chunk: break

        recieved += data_chunk

    # Send the data back with the REPLY prefix
    client.sendall(b'REPLY: ' + recieved)

    # Close both socket connections and return the recieved data
    client.close()
    server_socket.close()
    return recieved


if __name__ == "__main__":
    print(
        serve_one(8888).decode()
    )
    pass
