# Author: Carson Angell
# Class: CS-4480
# Date: 9/18/2026

import socket
import time
import re as regex
from typing import Callable

from test_harness import MockOrigin

# Constants defined for all tests
TARGET_HOST = 'localhost'
PORTS = {
    'mock_origin': 19000,
    'clean': 2200,
    'buggy': 2100
}

# Method that was copied from Task A on Milestone 0. This is used in the tests below in order to make basic
# communication and have less boiler plate code.
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


# A helper class used to parse HTTP responses from raw text into objects. Makes testing for incorrect properties
# much easier, smaller and readable.
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


# A helper class used to parse HTTP requests from raw text into objects. Makes testing for incorrect properties
# much easier, smaller and readable.
class HTTPRequest:
    def __init__(self, body: bytes) -> None:
        self.raw = body.decode()
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



def test_one(port : int) -> bool:
    """
    Tests to make sure that the target proxy sends a 400 Bad Request error when receiving a request that's
    not using HTTP/1.0 protocol.

    - Successfully locates 1 bug
    """
    body = 'GET http://localhost:19000/ HTTP/$\r\n\r\n'

    if HTTPResponse( fetch( TARGET_HOST, port, body.replace('$', '1.1').encode() ) ).code != 400 : return True
    if HTTPResponse( fetch( TARGET_HOST, port, body.replace('$', '2.0').encode() ) ).code != 400 : return True
    if HTTPResponse( fetch( TARGET_HOST, port, body.replace('$', '3.0').encode() ) ).code != 400 : return True

    return False




def test_two(port : int) -> bool:
    """
    Tests to make sure that the target proxy sends a 400 Bad Request error when receiving a request that has
    malformed headers
    
    - Successfully locates 1 bug
    """
    body = b'GET http://localhost:19000/ HTTP/1.0\r\nUser-Agent : LinuxUser/1.0\r\n\r\n'
    response = HTTPResponse( fetch( TARGET_HOST, port, body ) )
    return response.code != 400




def test_three(port: int) -> bool:
    """
    Tests to make sure that the target proxy forwards the request using a relative URI path and not an
    absolute URI. Uses the mock origin to receive the request.
    
    - Successfully locates 1 bug
    """
    origin = MockOrigin(PORTS['mock_origin'])
    body = b'GET http://localhost:19000/path HTTP/1.0\r\n\r\n'
    received : HTTPRequest

    try:
        fetch( TARGET_HOST, port, body )
        if (origin.received is None): return True
        received = HTTPRequest( origin.received )
    finally:
        origin.close()

    return received.url != '/path'




def test_four(port: int) -> bool:
    """
    Tests to make sure that the target proxy forwards the request with a correct Host header.
    
    - Successfully locates 1 bug
    """
    origin = MockOrigin(PORTS['mock_origin'])
    body = b'GET http://localhost:19000/ HTTP/1.0\r\n\r\n'

    try:
        fetch( TARGET_HOST, port, body )
        if (origin.received is None): raise
        received = HTTPRequest( origin.received )
        if {'Host': 'localhost'} not in received.headers: return True
    finally:
        origin.close()

    return False




def test_five(port: int) -> bool:
    """
    Tests to make sure that the target proxy forwards the request with a corrected and non-missing Connection header.
    
    - Successfully locates 1 bug
    """
    origin = MockOrigin(PORTS['mock_origin'])
    body = b'GET http://localhost:19000/ HTTP/1.0\r\nConnection: keep-alive\r\n\r\n'

    try:
        fetch( TARGET_HOST, port, body )
        if (origin.received is None): raise
        received = HTTPRequest( origin.received )
        if {'Connection': 'close'} not in received.headers: return True
    finally:
        origin.close()

    return False



def test_six(port: int) -> bool:
    """
    Tests to make sure that the target proxy responds with the entire response no matter how big it is.
    For this test, it expected an 8KB long list of a repeating character as its response body.

    - Successfully locates 1 bug
    """
    expected_response_length = 8192
    origin = MockOrigin( PORTS['mock_origin'], body_size = expected_response_length )
    body = b'GET http://localhost:19000/ HTTP/1.0\r\n\r\n'

    try:
        response = HTTPResponse( fetch( TARGET_HOST, port, body ) )
        if (origin.received is None): raise

        if len(response.message) - 1 != expected_response_length: return True
    finally:
        origin.close()

    return False


# Runs all the tests in a loop with correct timing, port targeting and nicely formatted print statements.
if __name__ == "__main__":
    tests : list[ Callable[[int], bool] ] = [
        test_one,
        test_two,
        # test_three,
        # test_four,
        # test_five,
        # test_six
    ]

    for test in tests:
        print(f'Running {test.__name__}')
        print('Test Result for Buggy  ->  ' + str( test( PORTS['buggy'] ) ))
        time.sleep(0.5)

        print('Test Result for Clean  ->  ' + str( test( PORTS['clean'] ) ))
        time.sleep(0.5)

        print()
