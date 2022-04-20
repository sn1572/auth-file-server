import sys
import os
import random
sys.path.insert(0, '..')
import file_server as fs


_test_path = os.path.abspath('../file_server.py')
_test_length = os.path.getsize(_test_path)


def excprint(string):
    raise Exception(string)


def test_partial_response_1():
    'Basic test of length. Does it really return 2000 bytes?'
    response = fs.partial_response(_test_path, 0, None, 2000)
    assert len(response.data) == 2000
    assert response.status == '206 PARTIAL CONTENT'
    headers = response.headers
    assert headers['Content-Length'] == '2000'
    assert headers['Content-Range'] == f"bytes 0-1999/{_test_length}"
    assert headers['Accept-Ranges'] == 'bytes'


def test_partial_response_2():
    '''
    Does it return the right number of bytes when arbitrary start and
    length parameters are provided?
    '''
    start = random.randint(10, int(0.1 * _test_length))
    length = random.randint(0, _test_length - 1 - start)
    response = fs.partial_response(_test_path, start, None, length)
    assert len(response.data) == length
    assert response.status == '206 PARTIAL CONTENT'
    headers = response.headers
    assert headers['Content-Length'] == str(length)
    right_length = f"bytes {start}-{start+length-1}/{_test_length}"
    assert headers['Content-Range'] == right_length
    assert headers['Accept-Ranges'] == 'bytes'


def test_partial_response_3():
    'Does it actually return the bytes it says it does?'
    start = random.randint(10, int(0.1 * _test_length))
    length = random.randint(0, _test_length - 1 - start)
    response = fs.partial_response(_test_path, start, None, length)
    with open(_test_path, 'rb') as fd:
        fd.seek(start)
        data = fd.read(length)
    assert response.data == data


def test_fd_seek():
    'Are we using seek right?'
    with open(_test_path, 'rb') as fd:
        data = fd.read(20)
        fd.seek(4)
        five_to_fifteen = fd.read(10)
    assert(five_to_fifteen) == data[4:14]
