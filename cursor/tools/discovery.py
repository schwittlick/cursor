"""

A tool that scans all serial ports for HPGL-compatible plotters

Adjust the baud-rate, serial timeout & other parameters in case a plotter is not detected

The script will print a list of available plotters, it's serial ports and model number

"""

import logging
import subprocess
import threading

import serial.tools.list_ports

from cursor.hpgl import read_until_char, OUTPUT_DIMENSIONS, MODEL_IDENTIFICATION


def async_discover(
        serial_port: str,
        baudrate: int = 9600,
        stopbits: tuple = serial.STOPBITS_ONE,
        bytesize: tuple = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        xonxoff: bool = False,
        timeout: float = 1.0,
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
        ser.write(f"{MODEL_IDENTIFICATION}".encode())
        """
        Using another command like @OUTPUT_IDENTIFICATION is not possible, because models
        like the HP7470A and all Roland DXY plotters do not respond to this command. Using the 
        classic HPGL command OI; @MODEL_IDENTIFICATION should work for all models. There might 
        be only one difference that the machines only respond to OI; when they are finished 
        setting up. In the case of a HP7550 the machine will not reply it's model before the 
        paper is loaded.
        """
        ret = read_until_char(ser, timeout)
        model = ret.strip()
        if len(model) > 0:
            ser.write(f"{OUTPUT_DIMENSIONS}".encode())
            ret = read_until_char(ser, timeout)
            space = ret.strip()

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
        timeout=0.5,
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
