import logging

import serial

from cursor.hpgl import read_until_char


def send_and_receive(serial_connection: serial.Serial, command: str, timeout: float = 1.0) -> str | None:
    """
    Wrapper function to wait for an answer from a serial port.

    Works with most plotters, once the communication works, it will return a CR after an answer.
    """
    try:
        serial_connection.write(command.encode())
        logging.debug(f"{serial_connection.port} <- {command}")
        received_data = read_until_char(serial_connection, timeout=timeout)
        logging.debug(f"{serial_connection.port} -> {received_data}")
        if len(received_data) > 0:
            return received_data
    except serial.SerialException as e:
        logging.error(f"Error: {str(e)}")

    return None
