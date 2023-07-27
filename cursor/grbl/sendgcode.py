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


class GCODEStreamer:
    def __init__(self, plotter: serial.Serial):
        self.HOME = (-4990.0, -10.0, -10.0)

        self.plotter = plotter

        # Wake up grbl
        self.plotter.write("\r\n\r\n".encode())
        time.sleep(2)
        self.plotter.flushInput()

    def stream(self, gcode: list[str]) -> None:
        ok, error = self.home()

        if not ok:
            logger.fail("Homing didnt work. Abort")
            return

        for line in gcode:
            line = line.strip()
            ok, error = self.send(line)
            if not ok:
                if not error.startswith("[HLP:"):
                    logger.fail(f"GRBL returned {error}")
                    logger.fail(f"While sending {line}")
                    break
            else:
                # e.g. G01 X10.00 Y-10.00 F2000
                if "X" in line and "Y" in line:
                    xy = parse_xy(line)
                    target = self.HOME[0] + xy[0], self.HOME[1] + xy[1]
                    pos = self.current_position()
                    while target[0] != pos[0] and target[1] != pos[1]:
                        time.sleep(0.5)
                        pos = self.current_position()
                # e.g. G01 Z0.0 F1000
                elif "Z" in line:
                    z = parse_z(line)
                    target = self.HOME[2] + z
                    pos = self.current_position()
                    while target != pos[2]:
                        time.sleep(0.5)
                        pos = self.current_position()

    def current_position(self) -> tuple[float, float, float]:
        self.plotter.write("?".encode())
        time.sleep(0.1)
        status = self.plotter.readline().decode()
        # logger.info(f"status: {status}")
        try:
            status_fields = status.split("|")
            pos = status_fields[1][5:]
            xyz = pos.split(",")
            return float(xyz[0]), float(xyz[1]), float(xyz[2])
        except IndexError:
            logger.fail(f"Failed to get info from status {status}")
            return 0, 0, 0

    def home(self) -> tuple[bool, str]:
        return self.send("$H")

    def send(self, cmd: str) -> tuple[bool, str]:
        logger.info(f"sending: {cmd}")
        self.plotter.write(f"{cmd}\n".encode())
        time.sleep(0.05)
        is_ok = self.plotter.readline().decode()
        return is_ok.startswith("ok"), is_ok


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

    gcode = open(args.file, 'r').readlines()
    plotter = serial.Serial(args.port, 115200, timeout=10)

    streamer = GCODEStreamer(plotter)
    streamer.stream(gcode)

    plotter.close()
