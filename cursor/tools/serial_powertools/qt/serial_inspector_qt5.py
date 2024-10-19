import logging
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import serial
import serial.tools.list_ports

from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.plotter.plotter import HPGLPlotter
from cursor.tools.serial_powertools.seriallib import AsyncSerialSender

from bruteforce_qt5 import run_brute_force


class SerialInspector(QObject):
    connection_status_changed = pyqtSignal(str)
    command_sent = pyqtSignal(str)
    file_progress_updated = pyqtSignal(int, int)
    plotter_model_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.serial_connection = serial.Serial()
        self.bruteforce_threads = []
        self.async_sender = None

    def check(self) -> bool:
        return self.serial_connection.is_open

    def send_command(self, command: str):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        commands = tokenizer(command)

        def progress_cb(command_idx: int):
            pass

        self.async_sender.add_commands(commands, progress_cb)
        logging.info(f"Sent: {command}: {self.serial_connection.port}")
        self.command_sent.emit(command)

    def insert_command(self, command: str):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        if self.async_sender is None:
            logging.warning("No active job to insert command into.")
            return

        commands = tokenizer(command)
        self.async_sender.insert_commands(commands)
        logging.info(f"Inserted command: {command}")
        self.command_sent.emit(command)

    def disconnect_serial(self):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        self.serial_connection.close()
        if self.async_sender:
            self.async_sender.stop()
        logging.info(f"Disconnected from {self.serial_connection.port}")
        self.connection_status_changed.emit("Disconnected")

    def connect_serial(self, port: str, baud: int):
        logging.info(f"Attempting to connect to {port} at {baud} baud")

        if self.check():
            logging.warning(
                f"Already connected to {self.serial_connection.port}")
            return

        try:
            self.serial_connection = serial.Serial(port, baud, timeout=1)
            logging.info(
                f"Serial connection established to {self.serial_connection.port}")

            self.connection_status_changed.emit("Connected")
            logging.info(f"Connected to {self.serial_connection.port}")

            plotter = HPGLPlotter(self.serial_connection)
            logging.info("HPGLPlotter instance created")

            self.async_sender = AsyncSerialSender(plotter)
            logging.info("AsyncSerialSender instance created")

            self.async_sender.do_software_handshake = True
            self.async_sender.command_batch = 1
            logging.info("AsyncSerialSender configured")

            self.async_sender.start()
            logging.info("AsyncSerialSender started")

        except serial.SerialException as e:
            logging.error(f"Failed to connect to {port}: {str(e)}")
            self.connection_status_changed.emit(f"Connection failed: {str(e)}")
        except Exception as e:
            logging.error(
                f"Unexpected error while connecting to {port}: {str(e)}")
            self.connection_status_changed.emit(
                "Connection failed: Unexpected error")

        self.async_sender = AsyncSerialSender(plotter)
        self.async_sender.do_software_handshake = True
        self.async_sender.command_batch = 1
        self.async_sender.start()

    def stop_send_serial_file(self):
        self.async_sender.abort()
        logging.info(f"Stopped async sender. {self.async_sender.plotter}")

    def send_serial_file(self, file_path: str):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        logging.info(f"Sending {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            hpgl_text = file.read()

        commands = tokenizer(hpgl_text)

        def progress_cb(command_idx: int):
            self.file_progress_updated.emit(command_idx, len(commands))

        self.async_sender.add_commands(commands, progress_cb)

    def start_bruteforce_progress(self, port: str, timeout: float):
        # stopping previously running bruteforce threads
        for thread in self.bruteforce_threads:
            thread.stopped = True
            thread.join()

        baud_rates = [150, 300, 600, 1200, 2400, 4800, 9600, 19200, 115200]
        parities = [serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_EVEN]
        stop_bits = [serial.STOPBITS_ONE, serial.STOPBITS_TWO]
        xonxoff = [True, False]
        byte_sizes = [serial.SEVENBITS, serial.EIGHTBITS]

        message = "OI;"

        self.bruteforce_threads = run_brute_force([port], baud_rates, parities, stop_bits, xonxoff,
                                                  byte_sizes, message, timeout)

    def stop_bruteforce_progress(self):
        for thread in self.bruteforce_threads:
            thread.stopped = True
            thread.join()

        logging.info("Stopped bruteforce threads")

    def get_plotter_model(self):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        model = self.async_sender.plotter.identify()
        self.plotter_model_received.emit(model)


class BruteforceWorker(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, inspector: SerialInspector, port: str, timeout: float):
        super().__init__()
        self.inspector = inspector
        self.port = port
        self.timeout = timeout

    def run(self):
        self.inspector.start_bruteforce_progress(self.port, self.timeout)
        self.finished.emit()

    def stop(self):
        self.inspector.stop_bruteforce_progress()
