import socket
import time
import re as regex
from typing import Callable

from M1_Handout.test_harness import MockOrigin

TARGET_HOST = 'localhost'
MOCK_ORIGIN_PORT = 19000
PORTS = {
    'clean': 2100,
    'buggy': 2200
}


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
        else: response += data_chunk

    # Close the connection and return the response.
    client_socket.close()
    return response


class HTTPResponse:
    def __init__(self, body: bytes) -> None:
        self.raw = body.decode()
        tokens = self.raw.split('\r\n')

        self.protocol : str = regex.findall(r"HTTP\/[0-9].[0-9]", tokens[0])[0]
        self.code : int = int( regex.findall(r" [0-9]{3} ", tokens[0])[0].strip() )
        self.message : str = ''
        self.headers : list[dict[str, str]] = []

        for i in range(1, tokens.index('')):
            key = tokens[i].split(':')[0].strip()
            value = tokens[i].split(':')[1].strip()
            self.headers.append({ key: value })

        for token in tokens[::-1]:
            if token == '': break

            self.message = token + '\n' + self.message

    def __str__(self) -> str:
        return self.raw.replace('\r\n', '\\r\\n')


class HTTPRequest:
    def __init__(self, body: str) -> None:
        self.raw = body
        tokens = self.raw.split('\r\n')

        self.method : str = tokens[0].split(' ')[0]
        self.url : str = tokens[0].split(' ')[1]
        self.protocol : str = tokens[0].split(' ')[2]
        self.headers : list[dict[str, str]] = []

        for i in range(1, len(tokens) - 1):
            if tokens[i] == '': break
            key = tokens[i].split(':')[0].strip()
            value = tokens[i].split(':')[1].strip()
            self.headers.append({ key: value })

    def __str__(self) -> str:
            return self.raw.replace('\r\n', '\\r\\n')


def test_one(port: int) -> bool: # Testing basic request to make sure it knows a valid request
    body = b'GET http://localhost:19000/ HTTP/1.0\r\n\r\n'
    response = HTTPResponse( fetch( TARGET_HOST, port, body ) )
    return response.code != 200 and response.code != 502



def test_two(port : int) -> bool: # Testing unsupported HTTP protocol version # - 1 Discrepenecy Found
    body = b'GET http://localhost:19000/ HTTP/1.1\r\n\r\n'
    response = HTTPResponse( fetch( TARGET_HOST, port, body ) )
    return response.code != 400



def test_three(port : int) -> bool: # Testing malformed headers # - 1 Discrepency Found
    body = b'GET http://localhost:19000/ HTTP/1.0\r\nUser-Agent : LinuxUser/1.0\r\n\r\n'
    response = HTTPResponse( fetch( TARGET_HOST, port, body ) )
    return response.code != 400



def test_four(port: int) -> bool: # Testing to make sure path is relative on origin # - 1 Descrepency Found
    origin = MockOrigin(MOCK_ORIGIN_PORT)
    body = b'GET http://localhost:19000/path HTTP/1.0\r\n\r\n'

    try:
        fetch( TARGET_HOST, port, body )
        if (origin.received is None): raise
        received = HTTPRequest( origin.received.decode() )
    finally:
        origin.close()

    return received.url != '/path'



def test_five(port: int) -> bool: # Testing to make mock origin receives host header # - 1 Descrepency Found
    origin = MockOrigin(MOCK_ORIGIN_PORT)
    body = b'GET http://localhost:19000/ HTTP/1.0\r\n\r\n'

    try:
        fetch( TARGET_HOST, port, body )
        if (origin.received is None): raise
        received = HTTPRequest( origin.received.decode() )
        if {'Host': 'localhost'} not in received.headers: return True
    finally:
        origin.close()

    return False



def test_six(port: int) -> bool: # Testing to make mock origin recieves changed connection header # - 1 Descrepency Found
    origin = MockOrigin(MOCK_ORIGIN_PORT)
    body = b'GET http://localhost:19000/ HTTP/1.0\r\nConnection: keep-alive\r\n\r\n'

    try:
        fetch( TARGET_HOST, port, body )
        if (origin.received is None): raise
        received = HTTPRequest( origin.received.decode() )
        if {'Connection': 'close'} not in received.headers: return True
    finally:
        origin.close()

    return False


    # test_one()
# def test7():
#     print( 'Performing Test #7:' )
#     body = "GET http://localhost:19000/ HTTP/1.0\r\n"
#     ports = {'clean': CLEAN_PORT, 'buggy': BUGGY_PORT}

#     for name, port in ports.items():
#         ORIGIN = MockOrigin(19000)

#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         client_socket.connect((TARGET_HOST, port))
#         client_socket.sendall(body.encode())

#         print(f'Origin Recieved {name.capitalize()} Before Complete  ->   ' + str(ORIGIN.received))
    
#         client_socket.sendall(b'\r\n')
#         client_socket.shutdown(socket.SHUT_WR)

#         response = b''
#         while True:
#             data_chunk = client_socket.recv(2048)
    
#             if not data_chunk: break
#             else: response += data_chunk
    
#         print(f'Origin Recieved {name.capitalize()} After Complete  ->   ' + str(ORIGIN.received))
#         print(f'{name.capitalize()} Response  ->  ' + response.decode().replace('\r\n', '\\r\\n'))

#         client_socket.close()
#         ORIGIN.close()

#         time.sleep(1)


if __name__ == "__main__":
    tests : list[ Callable[[int], bool] ] = [
        test_one,
        test_two,
        test_three,
        test_four,
        test_five,
        test_six
    ]

    for test in tests:
        print('Test Result for Buggy  ->  ' + str( test( PORTS['buggy'] ) ))
        time.sleep(0.5)

        print('Test Result for Clean  ->  ' + str( test( PORTS['clean'] ) ))
        time.sleep(0.5)

        print()
