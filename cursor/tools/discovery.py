"""

A tool that scans all serial ports for HPGL-compatible plotters

Adjust the baud-rate, serial timeout & other parameters in case a plotter is not detected

The script will print a list of available plotters, it's serial ports and model number

"""

import logging
import subprocess
import threading

import serial.tools.list_ports

from cursor.hpgl import read_until_char, OUTPUT_IDENTIFICATION, OUTPUT_DIMENSIONS


def async_discover(
    serial_port: str,
    baudrate: int = 9600,
    stopbits: tuple = serial.STOPBITS_ONE,
    bytesize: tuple = serial.EIGHTBITS,
    parity: str = serial.PARITY_NONE,
    xonxoff: bool = False,
    timeout: float = 5,
) -> tuple[str, str] | None:
    ser = serial.Serial(
        port=serial_port,
        baudrate=baudrate,
        stopbits=stopbits,
        bytesize=bytesize,
        parity=parity,
        xonxoff=xonxoff,
        timeout=timeout,
    )
    try:
        ser.write(f"{OUTPUT_IDENTIFICATION}".encode())
        ret = read_until_char(ser).split(",")[0]
        model = ret.strip()
        if len(model) > 0:
            ser.write(f"{OUTPUT_DIMENSIONS}".encode())
            ret = read_until_char(ser)
            space = ret.strip()
            # TODO: Machine e.g. 7470A does not return output dimensions..
            # With this current logic the machine is not detected..

            ser.close()
            logging.info(f"Discovery {serial_port} -> {model} (OH: {space})")

            return serial_port, model
        ser.close()
        return None
    except serial.SerialException:
        # If the port is already open, skip to the next one
        return None
    except OSError as e:
        print(e)
        return None


def discover(
    baudrate=9600,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    xonxoff=False,
    timeout=1.5,
) -> set[tuple[str, str]]:
    ports = list(serial.tools.list_ports.comports())
    data = []

    # check if port is already open from another application
    # better do that instead of troubling the sendhpgl communication protocol
    # >> lsof /dev/ttyUSB0
    # returns nothing when the port is not used by another application
    ports = [
        port.device
        for port in ports
        if not len(subprocess.getoutput(f"lsof {port.device}")) > 0
    ]

    threads = []

    for port in ports:
        thread = threading.Thread(
            target=lambda: data.append(
                async_discover(
                    port,
                    baudrate,
                    stopbits=stopbits,
                    bytesize=bytesize,
                    parity=parity,
                    xonxoff=xonxoff,
                    timeout=timeout,
                )
            )
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    data = set(list(filter(lambda x: x is not None, data)))

    return data


if __name__ == "__main__":
    discover()
