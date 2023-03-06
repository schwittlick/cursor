from tools.octet.client import Client


class Plotter:
    def __init__(self, ip, port, serial_port, baud, timeout):
        self.serial_port = serial_port
        self.baud = baud
        self.timeout = timeout
        self.ip = ip
        self.port = port
        self.client = Client(self.ip, self.port)
        self.is_connected = False

    def __prefix(self):
        return f"{self.serial_port},{self.baud},{self.timeout},"

    def connect(self):
        self.is_connected = self.client.connect()

    def disconnect(self):
        self.client.close()
        self.is_connected = False

    def get_model(self):
        self.client.send(f"{self.__prefix()}OI;")

    def get_bounds(self):
        self.client.send(f"{self.__prefix()}OH;")

    def is_open_serial(self):
        self.client.send(f"{self.__prefix()}IS_OPEN")

    def open_serial(self):
        self.client.send(f"{self.__prefix()}OPEN")

    def close_serial(self):
        self.client.send(f"{self.__prefix()}CLOSE")

    def recv(self):
        return self.client.receive_feedback()
