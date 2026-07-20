"""

A tool that scans all serial ports for HPGL-compatible plotters

Adjust the baud-rate, serial timeout & other parameters in case a plotter is not detected

The script will print a list of available plotters, it's serial ports and model number

"""

import logging
import subprocess
import threading
import time

import serial.tools.list_ports

from cursor.hpgl import MODEL_IDENTIFICATION, OUTPUT_DIMENSIONS, read_until_char


def async_discover(
    serial_port: str,
    baudrate: int = 9600,
    stopbits: tuple = serial.STOPBITS_ONE,
    bytesize: tuple = serial.EIGHTBITS,
    parity: str = serial.PARITY_NONE,
    xonxoff: bool = False,
    timeout: float = 1.0,
) -> tuple[str, str] | None:
    try:
        ser = serial.Serial(
            port=serial_port,
            baudrate=baudrate,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            xonxoff=xonxoff,
            timeout=timeout,
        )
        ser.write(f"{MODEL_IDENTIFICATION}".encode())
        """
        Using another command like @OUTPUT_IDENTIFICATION is not possible, because models
        like the HP7470A and all Roland DXY plotters do not respond to this command. Using the
        classic HPGL command OI; @MODEL_IDENTIFICATION should work for all models. There might
        be only one difference that the machines only respond to OI; when they are finished
        setting up. In the case of a HP7550 the machine will not reply it's model before the
        paper is loaded.
        """
        ret = read_until_char(ser, timeout=timeout)
        model = ret.strip()
        if len(model) > 0:
            ser.write(f"{OUTPUT_DIMENSIONS}".encode())
            ret = read_until_char(ser, timeout=timeout)
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
        if subprocess.call(["fuser", port.device], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0
    ]

    threads = []

    for port in ports:
        thread = threading.Thread(
            target=lambda p=port: data.append(
                async_discover(
                    p,
                    baudrate,
                    stopbits=stopbits,
                    bytesize=bytesize,
                    parity=parity,
                    xonxoff=xonxoff,
                    timeout=timeout,
                )
            ),
            daemon=True,
        )

        threads.append(thread)
        thread.start()

    # Bound the total wait. The probe threads run in parallel and each is internally
    # bounded by its own read timeout, so a well-behaved port resolves within roughly
    # 2 * timeout (one read for the model, one for the dimensions). A single misbehaving
    # port (e.g. a phantom /dev/ttyS* that opens but then stops honoring its read
    # timeout) must not be able to freeze discovery indefinitely, so we abandon
    # stragglers after a hard deadline. Threads are daemons, so an abandoned one won't
    # block process shutdown.
    deadline = time.monotonic() + timeout * 3 + 0.5
    for thread in threads:
        thread.join(timeout=max(0.0, deadline - time.monotonic()))

    data = set(filter(None, list(data)))

    return data


if __name__ == "__main__":
    discover()
