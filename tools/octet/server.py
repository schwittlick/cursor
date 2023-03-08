import socket
import threading
import serial
import wasabi
import time

logger = wasabi.Printer(pretty=True, no_print=False)


class SerialConnection:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.current_buffer = ""

    def open(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def is_open(self):
        if self.serial:
            return self.serial.is_open

        return False

    def close(self):
        self.serial.close()

    def readline(self):
        return self.serial.readline().decode("utf-8")

    def read_until(self, expected):
        buffer = bytearray()
        while True:
            # Read one byte from the serial connection
            byte = self.serial.read(1)
            if not byte:
                # If the read timed out or was otherwise unsuccessful, return None
                return None
            # Append the byte to the buffer
            buffer += byte
            # Check if the expected string is in the buffer
            if expected in buffer:
                # If it is, return the bytes up to and including the expected string
                return buffer[:buffer.index(expected) + len(expected)]

    def write(self, data):
        self.serial.write(data)
        self.serial.flushOutput()

    def check_avail(self):
        self.serial.write(b'\x1B.B')
        self.serial.flushOutput()
        b = b''
        n = 0
        while b != b'\r':
            if len(b) > 0:
                n = n * 10 + b[0] - 48
            b = self.serial.read()
        return n

    def buffer(self, data, chunk=255):
        pos = 0
        self.current_buffer = data
        while pos < len(self.current_buffer):
            #logger.info(f"missing to send: {self.current_buffer[pos:]}")
            avail = self.check_avail()
            logger.info(f"free mem: {avail}")
            if avail < chunk:
                time.sleep(0.1)
                continue

            end = pos + avail
            if len(self.current_buffer) - pos < avail:
                end = len(self.current_buffer)

            self.serial.write(self.current_buffer[pos:end].encode("utf-8"))
            self.serial.flushOutput()
            pos = end


class Server:
    MAX_SERIAL_CONNECTIONS = 8

    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.clients = []
        self.serial_connections = []

    def get_serial_connection(self, port):
        # Check if a serial connection with the same port already exists
        for conn in self.serial_connections:
            if conn.port == port:
                return conn
        # If not, create a new serial connection if the max limit is not reached
        if len(self.serial_connections) < Server.MAX_SERIAL_CONNECTIONS:
            conn = SerialConnection(port, 9600, 1)
            self.serial_connections.append(conn)
            return conn
        else:
            return None

    def listen(self):
        self.socket.listen()
        logger.good(f"Server is listening on {self.host}:{self.port}")
        while True:
            conn, addr = self.socket.accept()
            logger.good(f"Connected by {addr}")
            self.clients.append(conn)
            client_thread = threading.Thread(target=self.handle_client, args=(conn,))
            client_thread.start()

    def handle_client(self, socket_connection):
        with socket_connection:
            while True:
                try:
                    # Read the first 4 bytes to get the message length
                    raw_msglen = self.recvall(socket_connection, 4)
                    if not raw_msglen:
                        break
                    msglen = int.from_bytes(raw_msglen, 'big')
                    # Read the message data
                    data = self.recvall(socket_connection, msglen)
                    if not data:
                        break
                    logger.good(f"Received from {socket_connection.getpeername()}: {data.decode()}")
                    # Extract serial connection parameters from message
                    params = data.decode().split("#")
                    if len(params) != 4:
                        logger.fail(f"Invalid message format: {data.decode()}")
                        continue
                    port = params[0]
                    baudrate = int(params[1])
                    timeout = float(params[2])
                    command = params[3]
                    # Connect to serial port
                    try:
                        serial_connection = self.get_serial_connection(port)
                        if serial_connection is None:
                            feedback = "Error: Max number of serial connections reached"
                            self.send_feedback(socket_connection, False, feedback)
                            continue

                        # Do something with the serial connection
                        if command == "CLOSE":
                            if serial_connection.is_open():
                                serial_connection.close()
                                self.serial_connections.remove(serial_connection)
                                self.send_feedback(socket_connection, True, "CLOSED")
                                continue
                            elif serial_connection in self.serial_connections:
                                self.serial_connections.remove(serial_connection)
                                self.send_feedback(socket_connection, True, "ONLY REMOVED")
                                continue

                            self.send_feedback(socket_connection, False, "NOT REGISTERED")
                        elif command.startswith("DATA"):
                            data = command[4:]
                            is_open = serial_connection.is_open()
                            if not is_open:
                                continue
                            serial_connection.buffer(data)
                            self.send_feedback(socket_connection, True,
                                               f"SUCCESSFULLY SENT DATA")
                        elif command == "OPEN":
                            serial_connection.baudrate = baudrate
                            serial_connection.timeout = timeout
                            serial_connection.open()
                            is_open = serial_connection.is_open()
                            if is_open:
                                self.send_feedback(socket_connection, True,
                                                   f"OPENING SERIAL {serial_connection.port} SUCCEEDED")
                            else:
                                self.send_feedback(socket_connection, False,
                                                   f"OPENING SERIAL  {serial_connection.port} FAILED")
                        elif command == "IS_OPEN":
                            is_open = serial_connection.is_open()
                            if is_open:
                                self.send_feedback(socket_connection, True, f"SERIAL {serial_connection.port} IS OPEN")
                            else:
                                self.send_feedback(socket_connection, False,
                                                   f"SERIAL {serial_connection.port} IS NOT OPEN")
                        elif command == "OH;":
                            if serial_connection.is_open():
                                serial_connection.write(b"OH;\r\n")
                                response = serial_connection.readline()
                                if response:
                                    feedback = response.strip()
                                    self.send_feedback(socket_connection, True, feedback)
                                else:
                                    self.send_feedback(socket_connection, False, "SERIAL PORT DID NOT RESPOND")
                            else:
                                self.send_feedback(socket_connection, False, "SERIAL PORT IS NOT OPEN")
                        elif command == "OI;":
                            if serial_connection.is_open():
                                serial_connection.write(b"OI;\r\n")
                                response = serial_connection.readline()
                                if response:
                                    feedback = response.strip()
                                    self.send_feedback(socket_connection, True, feedback)
                                else:
                                    self.send_feedback(socket_connection, False, "SERIAL PORT DID NOT RESPOND")
                            else:
                                self.send_feedback(socket_connection, False, "SERIAL PORT IS NOT OPEN")

                    except serial.SerialException as e:
                        feedback = f"Error: {type(e)}"
                        logger.fail(feedback)
                        self.send_feedback(socket_connection, False, feedback)
                except ConnectionResetError:
                    logger.fail(f"Connection closed by {socket_connection.getpeername()}")

                    break
        logger.good(f"Disconnected {socket_connection}")
        self.clients.remove(socket_connection)

    def send_feedback(self, conn, success, message):
        # Send feedback message to client
        msg = f"{str(len(message)).ljust(8)} {1 if success else 0}{message}"
        logger.good(msg)
        conn.sendall(msg.encode())

    def recvall(self, conn, n):
        # Helper function to receive n bytes from a socket
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data


if __name__ == '__main__':
    server = Server('192.168.2.124')
    server.listen()
