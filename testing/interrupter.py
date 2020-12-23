import socket, getter


class Stream_Test(object):
    def __init__(self, address, port=5000):
        self.s = None
        self.address = address
        self.port = port

    def __enter__(self):
        msg = 'must close open socket connection first'
        assert self.s is None, msg
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.address, self.port))
        connection_string = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(self.address)
        connection_bytes = bytes(connection_string, 'utf-8')
        self.s.sendall(connection_bytes)
        return(self)

    def __call__(self, size=4096):
        assert self.s is not None, 'must open connection first'
        return(self.s.recv(size))

    def __exit__(self, a, b, c):
        self.s.close()
        self.s = None


if __name__ == '__main__':
    test = Stream_Test('192.168.1.16')
    with test as stream:
        stuff = stream()
        print(stuff)
