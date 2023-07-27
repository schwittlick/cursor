"""
jogging:
$J=X10.0 Y-1.5
"""
import time
from argparse import ArgumentParser

import serial
import wasabi

from cursor.grbl.parser import parse_xy, parse_z

logger = wasabi.Printer(pretty=True, no_print=False)

HOME = (-4990.0, -10.0, -10.0)


def home(s: serial.Serial) -> tuple[bool, str]:
    return send(s, "$H")


def send(plotter: serial.Serial, cmd: str) -> tuple[bool, str]:
    logger.info(f"sending: {cmd}")
    plotter.write(f"{cmd}\n".encode())
    time.sleep(0.05)
    is_ok = plotter.readline().decode()
    return is_ok.startswith("ok"), is_ok


def get_position(plotter: serial.Serial) -> tuple[float, float, float]:
    plotter.write(f"?".encode())
    time.sleep(0.1)
    status = plotter.readline().decode()
    # logger.info(f"status: {status}")
    try:
        status_fields = status.split("|")
        pos = status_fields[1][5:]
        xyz = pos.split(",")
        return float(xyz[0]), float(xyz[1]), float(xyz[2])
    except IndexError as ie:
        logger.fail(f"Failed to get info from status {status}")
        return 0, 0, 0


def stream_gcode(plotter: serial.Serial, gcode: list[str]) -> None:
    ok, error = home(plotter)

    if not ok:
        logger.fail("Homing didnt work. Abort")
        return

    for line in gcode:
        line = line.strip()
        ok, error = send(plotter, line)
        if not ok:
            if not error.startswith("[HLP:"):
                logger.fail(f"GRBL returned {error}")
                logger.fail(f"While sending {line}")
                break
        else:
            if "X" in line and "Y" in line:
                xy = parse_xy(line)
                target = HOME[0] + xy[0], HOME[1] + xy[1]
                pos = get_position(plotter)
                while target[0] != pos[0] and target[1] != pos[1]:
                    time.sleep(0.5)
                    pos = get_position(plotter)
            elif "Z" in line:
                z = parse_z(line)
                target = HOME[2] + z
                pos = get_position(plotter)
                while target != pos[2]:
                    time.sleep(0.5)
                    pos = get_position(plotter)


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
