import socket

def serve_one(port: int) -> bytes:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', port))
    server_socket.listen()

    client, _ = server_socket.accept()

    recieved = b''

    while True:
        data_chunk = client.recv(2048)
        if not data_chunk: break

        recieved += data_chunk

    client.sendall(b'REPLY: ' + recieved)

    client.close()
    server_socket.close()

    return recieved

print(serve_one(8888).decode())
