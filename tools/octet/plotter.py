from tools.octet.client import Client


class Plotter:
    def __init__(self, port, baud, timeout):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.ip = "192.168.2.124"
        self.client = Client(self.ip)
        self.is_connected = False

    def __prefix(self):
        return f"{self.port},{self.baud},{self.timeout},"

    def connect(self):
        self.client.connect()
        self.is_connected = True

    def disconnect(self):
        self.client.close()
        self.is_connected = False

    def is_open_serial(self):
        self.client.send(f"{self.__prefix()}IS_OPEN")

    def open_serial(self):
        self.client.send(f"{self.__prefix()}OPEN")

    def close_serial(self):
        self.client.send(f"{self.__prefix()}CLOSE")

    def recv(self):
        return self.client.receive_feedback()
