from tools.octet.client import Client


class Plotter:
    def __init__(self, port, baud, timeout):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.client = Client()

    def __prefix(self):
        return f"{self.port},{self.baud},{self.timeout},"

    def connect(self):
        self.client.connect()

    def disconnect(self):
        self.client.close()

    def open_serial(self):
        self.client.send(f"{self.__prefix()}OPEN")

    def close_serial(self):
        self.client.send(f"{self.__prefix()}CLOSE")

    def recv(self):
        return self.client.receive_feedback()
