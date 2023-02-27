import socket


class Client:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(1)

    def send(self, data):
        # Prepend the message length as 4 bytes in big-endian order
        msg = len(data).to_bytes(4, byteorder='big') + data.encode()
        self.socket.sendall(msg)

    def receive_feedback(self):
        s = self.recvall(8).decode().rstrip()
        # Receive the feedback message from the server
        data = self.recvall(int(s) + 2)  # a little extra
        data = data.decode()
        if not data:
            return None
        success = True if data[1] == "1" else False
        feedback = data[2:]
        return success, feedback

    def close(self):
        self.socket.close()

    def recvall(self, n):
        # Helper function to receive n bytes from a socket
        data = b''
        while len(data) < n:
            try:
                packet = self.socket.recv(n - len(data))
                if not packet:
                    return None
                data += packet
            except TimeoutError as e:
                print(e)
                return data
        return data


if __name__ == '__main__':
    client1 = Client()
    client1.connect()
    serial_params = "COM1,9600,500,OH;"
    client1.send(serial_params)
    print(client1.receive_feedback())
