"""
jogging:
$J=X10.0 Y-1.5
"""
import time
from argparse import ArgumentParser

import serial
import wasabi

logger = wasabi.Printer(pretty=True, no_print=False)


def home(s: serial.Serial) -> tuple[bool, str]:
    return send(s, "$H")


def send(plotter: serial.Serial, cmd: str) -> tuple[bool, str]:
    plotter.write(f"{cmd}\r\n".encode())
    is_ok = plotter.readline().decode()
    return is_ok.startswith("ok"), is_ok


def stream_gcode(plotter: serial.Serial, gcode: list[str]) -> None:
    ok, error = home(plotter)

    if not ok:
        logger.fail("Homing didnt work. Abort")
        return

    for line in gcode:
        line = line.strip()
        ok, error = send(plotter, line)
        if not ok:
            logger.fail(f"GRBL returned {error}")
            logger.fail(f"While sending {line}")
            break


if __name__ == '__main__':
    """
    todo: in parallel get current position
    only send new position data when current position has arrived
    
    add PSU to control laser
    essentially GCODE parser?
    """
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    args = parser.parse_args()

    plotter = serial.Serial(args.port, 115200, timeout=10)
    gcode = open(args.file, 'r').readlines()

    # Wake up grbl
    plotter.write("\r\n\r\n".encode())
    time.sleep(2)
    plotter.flushInput()

    stream_gcode(plotter, gcode)

    plotter.close()
