import logging
import threading

import dearpygui.dearpygui as dpg
import serial

from cursor.tools.serial_powertools.seriallib import send_and_receive


class BruteForcer(threading.Thread):
    def __init__(self,
                 serial_port: str,
                 baud_rates: list[int],
                 parities: list,
                 xonxoffs: list[bool],
                 byte_sizes: list,
                 stopbits: list[int],
                 timeout: float,
                 test_message: str):
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
                                dpg.set_value("bruteforce_progress", 0)
                                return
                            configuration_index += 1

                            progress_bar_value = configuration_index * self.progress_step_size
                            dpg.set_value("bruteforce_progress", progress_bar_value / 100)
                            try:
                                with serial.Serial(port=self.serial_port, baudrate=baud_rate,
                                                   xonxoff=xonxoff, stopbits=stopbit, parity=parity,
                                                   bytesize=byte_size,
                                                   timeout=self.timeout) as ser:
                                    response = send_and_receive(ser, self.test_message, self.timeout)
                                    if response:
                                        config = (baud_rate, xonxoff, stopbit, parity,
                                                  byte_size, response)
                                        logging.info(f"Detected {config}")
                                        responses.append(config)

                            except (serial.SerialException, serial.SerialTimeoutException) as e:
                                pass
                                # logging.error(f"Failed on {self.serial_port} at {baud_rate} baud: {e}")

        logging.info(f"{self.serial_port}: {responses}")


def run_brute_force(serial_ports: list[str],
                    baud_rates: list[int],
                    parities: list,
                    stop_bits: list,
                    xonxoff: list[bool],
                    byte_sizes: list,
                    test_message: str,
                    timeout: float = 1.0) -> list[BruteForcer]:
    """Each serial port is tested in its on thread, in parallel"""

    # calculate the worst-case duration of the test
    duration_approximated_seconds = len(baud_rates) * len(parities) * len(stop_bits) * len(xonxoff) * len(
        byte_sizes) * timeout
    logging.info(f"This bruteforce configuration will take ~{duration_approximated_seconds}s")

    bruteforcer_threads = []
    for port in serial_ports:
        thread = BruteForcer(port, baud_rates, parities=parities, xonxoffs=xonxoff, byte_sizes=byte_sizes,
                             stopbits=stop_bits, timeout=timeout,
                             test_message=test_message)
        thread.start()
        bruteforcer_threads.append(thread)

    return bruteforcer_threads


if __name__ == '__main__':
    ports = ["COM3", "COM3", "COM1"]  # List of serial ports to brute force
    baud_rates = [300, 900, 1200, 9600, 19200, 38400, 115200]  # Baud rates to try
    parities = [serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_EVEN]
    stop_bits = [serial.STOPBITS_ONE, serial.STOPBITS_TWO]
    xonxoff = [True, False]
    byte_sizes = [serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS]
    timeout = 0.1

    message = "OI;"

    run_brute_force(ports, baud_rates, parities, stop_bits, xonxoff, byte_sizes, message, timeout)
