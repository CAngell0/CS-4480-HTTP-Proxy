import socket

def fetch(host: str, port: int, message: bytes) -> bytes:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    client_socket.sendall(message)
    client_socket.sendall(message)

    client_socket.shutdown(socket.SHUT_WR)
    
    response = b''
    while True:
        data_chunk = client_socket.recv(2048)
        if not data_chunk: break

        response += data_chunk

    client_socket.close()

    return response

print(fetch('localhost', 8888, 'Hello World!'.encode()).decode())
