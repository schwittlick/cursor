import logging
import pathlib
import re
import typing

from cursor.collection import Collection
from cursor.path import Path

PEN_DOWN = 4.5
PEN_UP = 0.0


def parse_xy(gcode: str) -> typing.Union[tuple[float, float], None]:
    pattern = r'X(-?\d+\.\d+)\s+Y(-?\d+\.\d+)'
    matches = re.search(pattern, gcode)
    if matches:
        x_value = float(matches.group(1))
        y_value = float(matches.group(2))
        return x_value, y_value
    return None


def parse_z(gcode: str) -> typing.Union[float, None]:
    pattern = r'Z(-?\d+\.\d+)'
    matches = re.search(pattern, gcode)
    if matches:
        z_value = float(matches.group(1))
        return z_value
    return None


class GCODEParser:
    def __init__(self):
        """
        the gcode commands in a  file should be split by newlines e.g.

        G01 Z0.0 F1000
        G01 X0.00 Y0.00 F2000
        G01 Z4.5 F1000
        G01 X0.00 Y-0.00 F2000
        G01 X10.00 Y-0.00 F2000
        G01 Z0.0 F1000
        G01 X0.00 Y0.00 F2000

        """
        self.paths = Collection()

    def parse(self, gcode: typing.Union[pathlib.Path, list[str]]) -> Collection:
        if type(gcode) is list:
            gcode_cmds = gcode
        else:
            gcode_cmds = open(gcode.as_posix(), 'r', newline='').readlines()

        c = Collection()

        current_pen_down = False
        path = Path()

        for cmd in gcode_cmds:
            if cmd.startswith("G01"):
                if "X" in cmd and "Y" in cmd:
                    xy = parse_xy(cmd)
                    if xy:
                        if current_pen_down:
                            path.add(xy[0], xy[1])
                    else:
                        logging.error(f"Couldn't find X/Y values in {cmd}")
                elif "Z" in cmd:
                    z_value = parse_z(cmd)
                    if z_value:
                        current_pen_down = z_value == PEN_DOWN

                        if current_pen_down:
                            path.clear()
                        else:
                            if path.empty():
                                continue
                            c.add(path)
                    else:
                        logging.error(f"Couldn't find Z value in {cmd}")
                else:
                    logging.warning(f"Unknown parameters in cmd: {cmd}")

        return c
