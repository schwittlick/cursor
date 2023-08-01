"""
jogging:
$J=X10.0 Y-1.5
"""
import time
from argparse import ArgumentParser

import serial
import wasabi

from cursor.grbl.parser import parse_xy, parse_z
from cursor.tools.psu import PSU

logger = wasabi.Printer(pretty=True, no_print=False)


class GCODEStreamer:
    def __init__(self, plotter: serial.Serial, psu: PSU):
        self.HOME = (-4990.0, -10.0, 0.0)

        self.plotter = plotter
        self.psu = psu

        self.psu.open()
        self.psu.set_voltage_limit(5)
        self.psu.set_current_limit(0.5)
        self.psu.off()

        # Wake up grbl
        self.plotter.write("\r\n\r\n".encode())
        time.sleep(2)
        self.plotter.flushInput()

    def stream(self, gcode: list[str]) -> None:
        ok, error = self.home()

        if not ok:
            logger.fail("Homing didnt work. Abort")
            return

        current_delay = 0.0

        for line in gcode:
            line = line.strip()

            # checking for non-gcode commands
            if "AMP" in line:
                amp = float(line.rstrip()[3:])
                self.psu.set_current(amp)
                logger.info(f"Set laser amps to {amp}")
            elif "DELAY" in line:
                current_delay = float(line.rstrip()[5:])
                logger.info(f"Set laser delay to {current_delay}")
            elif "LASERON" in line:
                logger.info(f"Set laser ON")
                self.psu.on()
            elif "LASEROFF" in line:
                logger.info(f"Set laser ON")
                self.psu.off()
            else:
                ok, error = self.send(line)
                if not ok:
                    if not error.startswith("[HLP:"):
                        logger.fail(f"GRBL returned {error}")
                        logger.fail(f"While sending {line}")
                        break
                else:
                    # e.g. G01 X10.00 Y-10.00 Z4.5 F2000
                    if "X" in line and "Y" in line and "Z" in line:
                        xyz = parse_xy(line)
                        target = self.HOME[0] + xyz[0], self.HOME[1] + xyz[1], self.HOME[2] + xyz[2]
                        pos = self.current_position()
                        while target[0] != pos[0] and target[1] != pos[1] and target[2] != pos[2]:
                            time.sleep(0.1)
                            pos = self.current_position()
                    # e.g. G01 Z0.0 F1000
                    elif "Z" in line:
                        z = parse_z(line)
                        target = self.HOME[2] + z
                        pos = self.current_position()
                        while target != pos[2]:
                            time.sleep(0.1)
                            pos = self.current_position()

                        if z != 0.0:
                            logger.info(f"Delaying for {current_delay}")
                            time.sleep(current_delay)
                            current_delay = 0.0

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
    in order two draw a real 3d path (x, y, z) the hpgl parser needs to be rewritten
    also the hpgl parser/sender
    
    AMP1.0 -> set amp (send to psu)
    VOLT1.0 -> set volt (send to psu)
    LASER1 -> set laser on (send to psu)
    LASER0 -> turn laser off (send to psu)
    G01 X10.00 Y-10.00 Z2.00 F2000 -> XYZ pos (send to grbl)
    """
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('psu_port')
    parser.add_argument('file')
    args = parser.parse_args()

    gcode = open(args.file, 'r').readlines()
    plotter = serial.Serial(args.port, 115200, timeout=10)
    psu = PSU(args.psu_port)

    streamer = GCODEStreamer(plotter, psu)
    streamer.stream(gcode)

    plotter.close()
