import socket
import threading
import serial
import wasabi

logger = wasabi.Printer(pretty=True, no_print=False)

MAX_SERIAL_CONNECTIONS = 8


class SerialConnection:
    def __init__(self, port, baudrate, timeout):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def open(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def is_open(self):
        if self.serial:
            return self.serial.is_open()
        else:
            return False

    def close(self):
        self.serial.close()

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


class Server:
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
        if len(self.serial_connections) < MAX_SERIAL_CONNECTIONS:
            conn = SerialConnection(port, 9600, 1)
            self.serial_connections.append(conn)
            return conn
        else:
            return None

    def listen(self):
        self.socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            conn, addr = self.socket.accept()
            print(f"Connected by {addr}")
            self.clients.append(conn)
            client_thread = threading.Thread(target=self.handle_client, args=(conn,))
            client_thread.start()

    def handle_client(self, conn):
        with conn:
            while True:
                try:
                    # Read the first 4 bytes to get the message length
                    raw_msglen = self.recvall(conn, 4)
                    if not raw_msglen:
                        break
                    msglen = int.from_bytes(raw_msglen, 'big')
                    # Read the message data
                    data = self.recvall(conn, msglen)
                    if not data:
                        break
                    logger.info(f"Received from {conn.getpeername()}: {data.decode()}")
                    # Extract serial connection parameters from message
                    params = data.decode().split(",")
                    if len(params) != 4:
                        logger.info(f"Invalid message format: {data.decode()}")
                        continue
                    port = params[0]
                    baudrate = int(params[1])
                    timeout = int(params[2])
                    command = params[3]
                    # Connect to serial port
                    try:
                        ser_conn = self.get_serial_connection(port)
                        if ser_conn is None:
                            feedback = "Error: Max number of serial connections reached"
                            self.send_feedback(conn, False, feedback)
                            continue

                        # Do something with the serial connection
                        if command == "CLOSE":
                            if ser_conn.is_open():
                                ser_conn.close()
                                self.serial_connections.remove(ser_conn)
                                self.send_feedback(conn, True, "CLOSED")
                                continue
                            elif ser_conn in self.serial_connections:
                                self.serial_connections.remove(ser_conn)
                                self.send_feedback(conn, True, "ONLY REMOVED")
                                continue

                            self.send_feedback(conn, False, "NOT REGISTERED")
                        elif command == "OPEN":
                            ser_conn.baudrate = baudrate
                            ser_conn.timeout = timeout
                            ser_conn.open()
                            self.send_feedback(conn, True, "OPEN OK")
                        elif command == "OH;":
                            ser_conn.write(b"OH;\r\n")
                            response = ser_conn.read_until(b"\r\n").decode()
                            feedback = response.strip()
                            self.send_feedback(conn, True, feedback)
                        elif command == "OI;":
                            ser_conn.write(b"OI;\r\n")
                            response = ser_conn.read_until(b"\r\n").decode()
                            feedback = response.strip()
                            self.send_feedback(conn, True, feedback)
                    except serial.SerialException as e:
                        feedback = f"Error: {type(e)}"
                        logger.warn(feedback)
                        self.send_feedback(conn, False, feedback)
                except ConnectionResetError:
                    logger.warn(f"Connection closed by {conn.getpeername()}")

                    break
        self.clients.remove(conn)

    def send_feedback(self, conn, success, message):
        # Send feedback message to client
        msg = f"{str(len(message)).ljust(8)} {1 if success else 0}{message}"
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
