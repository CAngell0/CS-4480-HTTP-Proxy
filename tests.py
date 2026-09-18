import socket
import time

from M1_Handout.test_harness import MockOrigin

from toolkit.task_a_client import fetch

TARGET_HOST = 'localhost'
CLEAN_PORT = 2100
BUGGY_PORT = 2200

ORIGIN : MockOrigin

def formatted_fetch(body: str, port: int):
    return fetch(TARGET_HOST, port, body.encode()).decode().replace('\r\n', '\\r\\n')

def perform_response_test(body: str):
    print('Clean Response   ->   ' + formatted_fetch(body, CLEAN_PORT) )
    print('Buggy Response   ->   ' + formatted_fetch(body, BUGGY_PORT) )
    print()


def test1(): # Testing basic request to make sure it knows a valid request
    print( 'Performing Test #1:' )
    perform_response_test( "GET http://localhost:19000/ HTTP/1.0\r\n\r\n" )

def test2(): # Testing unsupported HTTP protocol version # - 1 Discrepenecy Found
    print( 'Performing Test #2:' )
    perform_response_test( "GET http://localhost:19000/ HTTP/1.1\r\n\r\n" )


def test3(): # Testing malformed headers # - 1 Discrepency Found
    print( 'Performing Test #3:' )
    perform_response_test( "GET http://localhost:19000/ HTTP/1.0\r\nUser-Agent : LinuxUser/1.0\r\n\r\n" )


def test4(): # Testing invalid HTTP method
    print( 'Performing Test #4:' )
    perform_response_test( "POST http://localhost:19000/ HTTP/1.0\r\n\r\n" )


def test5(): # Testing to make sure path is not absolute on origin # - 2 Descrepency Found
    print( 'Performing Test #5:' )
    body = "GET http://localhost:19000/path HTTP/1.0\r\n\r\n"
    ports = {'clean': CLEAN_PORT, 'buggy': BUGGY_PORT}

    for name, port in ports.items():
        ORIGIN = MockOrigin(19000)

        print(f'{name.capitalize()} Response   ->   ' + formatted_fetch(body, port))
        print(f'Origin Recieved {name.capitalize()}   ->   ' + str(ORIGIN.received))

        ORIGIN.close()
        time.sleep(1)
    print()

def test6(): # Testing to make sure path is not absolute on origin # - 1 Descrepency Found
    print( 'Performing Test #6:' )
    body = "GET http://localhost:19000/path HTTP/1.0\r\nConnection: keep-alive\r\n\r\n"
    ports = {'clean': CLEAN_PORT, 'buggy': BUGGY_PORT}

    for name, port in ports.items():
        ORIGIN = MockOrigin(19000)

        print(f'{name.capitalize()} Response   ->   ' + formatted_fetch(body, port))
        print(f'Origin Recieved {name.capitalize()}   ->   ' + str(ORIGIN.received))

        ORIGIN.close()
        time.sleep(1)
    print()


def test7():
    print( 'Performing Test #7:' )
    body = "GET http://localhost:19000/ HTTP/1.0\r\n"
    ports = {'clean': CLEAN_PORT, 'buggy': BUGGY_PORT}

    for name, port in ports.items():
        ORIGIN = MockOrigin(19000)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((TARGET_HOST, port))
        client_socket.sendall(body.encode())

        print(f'Origin Recieved {name.capitalize()} Before Complete  ->   ' + str(ORIGIN.received))
    
        client_socket.sendall(b'\r\n')
        client_socket.shutdown(socket.SHUT_WR)

        response = b''
        while True:
            data_chunk = client_socket.recv(2048)
    
            if not data_chunk: break
            else: response += data_chunk
    
        print(f'Origin Recieved {name.capitalize()} After Complete  ->   ' + str(ORIGIN.received))
        print(f'{name.capitalize()} Response  ->  ' + response.decode().replace('\r\n', '\\r\\n'))

        client_socket.close()
        ORIGIN.close()

        time.sleep(1)


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
