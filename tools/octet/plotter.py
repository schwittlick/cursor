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
        self.msg_delimiter = '#'
        self.type = None

    def __prefix(self):
        return f"{self.serial_port}{self.msg_delimiter}{self.baud}" \
               f"{self.msg_delimiter}{self.timeout}{self.msg_delimiter}"

    def connect(self):
        self.is_connected = self.client.connect()

    def disconnect(self):
        self.client.close()
        self.is_connected = False

    def send_data(self, data):
        self.client.send(f"{self.__prefix()}DATA{data}")
        self.client.set_timeout(0.5)
        return self.recv()

    def get_model(self):
        self.client.send(f"{self.__prefix()}OI;")
        return self.recv()

    def get_bounds(self):
        self.client.send(f"{self.__prefix()}OH;")
        return self.recv()

    def is_open_serial(self):
        self.client.send(f"{self.__prefix()}IS_OPEN")
        return self.recv()

    def open_serial(self):
        self.client.send(f"{self.__prefix()}OPEN")
        return self.recv()

    def close_serial(self):
        self.client.send(f"{self.__prefix()}CLOSE")
        return self.recv()

    def recv(self):
        return self.client.receive_feedback()
