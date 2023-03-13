import socket
import wasabi

logger = wasabi.Printer(pretty=False, no_print=False)


class Client:
    def __init__(self, host: str = 'localhost', port: int = 12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> bool:
        try:
            #logger.info(f"Connecting to")
            self.socket.connect((self.host, self.port))

            if self.socket.fileno() != -1:
                logger.info(f"Connected to {self.host}:{self.port}")
                return True
            else:
                logger.info(f"Not connected to {self.host}:{self.port}")
                return False
        except TimeoutError as te:
            logger.info(f"Not connected to {self.host}:{self.port} ({te})")
            return False

    def set_timeout(self, to: float):
        self.socket.settimeout(to)

    def send(self, data):
        # Prepend the message length as 4 bytes in big-endian order
        msg = len(data).to_bytes(4, byteorder='big') + data.encode()
        #logger.info(f"sending {data}")
        self.socket.sendall(msg)

    def receive_feedback(self):
        s = self.recvall(8)
        if s is None:
            return False, "No Feedback"
        s = s.decode().rstrip()
        # Receive the feedback message from the server
        data = self.recvall(int(s) + 2)  # a little extra
        data = data.decode()
        if not data:
            return False, "No Data"
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
