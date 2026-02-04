import logging

import serial
from PyQt5.QtCore import QThread, pyqtSignal

from cursor.tools.serial_powertools.seriallib import send_and_receive


class BruteForcer(QThread):
    progress_updated = pyqtSignal(float)
    result_found = pyqtSignal(tuple)
    finished = pyqtSignal()

    def __init__(
        self,
        serial_port: str,
        baud_rates: list[int],
        parities: list,
        xonxoffs: list[bool],
        byte_sizes: list,
        stopbits: list[int],
        timeout: float,
        test_message: str,
    ):
        super().__init__()

        self.baud_rates = baud_rates
        self.serial_port = serial_port
        self.parities = parities
        self.xonxoffs = xonxoffs
        self.byte_sizes = byte_sizes
        self.stopbits = stopbits
        self.timeout = timeout
        self.test_message = test_message

        self.options = len(baud_rates) * len(parities) * len(xonxoffs) * len(byte_sizes) * len(stopbits)
        self.progress_step_size = 100 / self.options

        self.stopped = False

    def run(self):
        responses = []
        configuration_index = 0

        for baud_rate in self.baud_rates:
            for parity in self.parities:
                for xonxoff in self.xonxoffs:
                    for byte_size in self.byte_sizes:
                        for stopbit in self.stopbits:
                            if self.stopped:
                                logging.info("Stopped Bruteforcer")
                                self.finished.emit()
                                return
                            configuration_index += 1

                            logging.info(
                                f"Checking {self.serial_port}:{baud_rate}. {parity}, {xonxoff}, {byte_size}, {stopbit}"
                            )

                            progress_bar_value = configuration_index * self.progress_step_size
                            self.progress_updated.emit(progress_bar_value)
                            try:
                                with serial.Serial(
                                    port=self.serial_port,
                                    baudrate=baud_rate,
                                    xonxoff=xonxoff,
                                    stopbits=stopbit,
                                    parity=parity,
                                    bytesize=byte_size,
                                    timeout=self.timeout,
                                ) as ser:
                                    response = send_and_receive(ser, self.test_message, self.timeout)
                                    if response:
                                        config = (baud_rate, xonxoff, stopbit, parity, byte_size, response)
                                        logging.info(f"Detected {config}")
                                        self.result_found.emit(config)
                                        responses.append(config)

                            except serial.SerialException, serial.SerialTimeoutException:
                                pass

        logging.info(f"{self.serial_port}: {responses}")
        self.finished.emit()

    def stop(self):
        self.stopped = True


def run_brute_force(
    serial_ports: list[str],
    baud_rates: list[int],
    parities: list,
    stop_bits: list,
    xonxoff: list[bool],
    byte_sizes: list,
    test_message: str,
    timeout: float = 1.0,
) -> list[BruteForcer]:
    """Each serial port is tested in its own thread, in parallel"""

    duration_approximated_seconds = (
        len(baud_rates) * len(parities) * len(stop_bits) * len(xonxoff) * len(byte_sizes) * timeout
    )
    logging.info(f"This bruteforce configuration will take ~{duration_approximated_seconds}s")

    bruteforcer_threads = []
    for port in serial_ports:
        thread = BruteForcer(
            port,
            baud_rates,
            parities=parities,
            xonxoffs=xonxoff,
            byte_sizes=byte_sizes,
            stopbits=stop_bits,
            timeout=timeout,
            test_message=test_message,
        )
        thread.start()
        bruteforcer_threads.append(thread)

    return bruteforcer_threads
