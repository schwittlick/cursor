import math
import time
import logging
from argparse import ArgumentParser

import serial
from tqdm import tqdm

from cursor.grbl.parser import parse_xy
from cursor.tools.psu import PSU

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

CHECK_FEEDBACK = True


class GCODEStreamer:
    def __init__(self, plotter: serial.Serial, psu: PSU):
        self.HOME = (-4990.0, -10.0, -10.0)

        self.plotter = plotter
        self.psu = psu

        self.psu.open()
        self.psu.set_voltage_limit(5)
        self.psu.set_current_limit(0.5)
        self.psu.off()

        # wake up grbl
        self.plotter.write("\r\n\r\n".encode())
        time.sleep(1.5)
        self.plotter.flushInput()

    def stream(self, gcode: list[str]) -> None:
        ok, error = self.home()

        if not ok:
            logging.critical(f"Homing didnt work: {ok}:{error}. Abort")
            return

        self.plotter.timeout = 0.5

        with tqdm(total=len(gcode)) as pbar:
            pbar.update(0)
            for line in gcode:
                line = line.strip()

                # checking for non-gcode commands
                if "AMP" in line:
                    amp = float(line.rstrip()[3:])
                    self.psu.set_current(amp)
                    logging.debug(f"Set laser amps to {amp}")
                elif "DELAY" in line:
                    delay = float(line.rstrip()[5:])
                    logging.debug(f"Laser delay to {delay}")
                    time.sleep(delay)
                elif "VOLT" in line:
                    volt = float(line.rstrip()[4:])
                    logging.debug(f"Set laser volt to {volt}")
                elif "LASERON" in line:
                    logging.debug("Laser ON")
                    self.psu.on()
                elif "LASEROFF" in line:
                    logging.debug("Laser OFF")
                    self.psu.off()
                else:
                    ok, error = self.send(line)
                    if not ok:
                        if not error.startswith("[HLP:"):
                            logging.error(f"GRBL returned {error}")
                            logging.error(f"While sending {line}")
                            break
                    else:
                        # e.g. G01 X10.00 Y-10.00 Z4.5 F2000
                        if "X" in line and "Y" in line and "Z" in line:
                            if CHECK_FEEDBACK:
                                xyz = parse_xy(line)
                                target_x = int(self.HOME[0] + xyz[0])
                                target_y = int(self.HOME[1] + xyz[1])
                                target_z = int(self.HOME[2] + xyz[2])
                                pos_x, pos_y, pos_z = self.current_position()

                                times = 0
                                while not math.isclose(target_x, pos_x) or \
                                        not math.isclose(target_y, pos_y) or \
                                        not math.isclose(target_z, pos_z):
                                    pos_x, pos_y, pos_z = self.current_position()
                                    times += 1
                pbar.update(1)

    def current_position(self) -> tuple[float, float, float]:
        self.plotter.write("?".encode())
        time.sleep(0.05)
        status = self.plotter.readline().decode()
        logging.debug(f"status: {status}")
        try:
            status_fields = status.split("|")
            pos = status_fields[1][5:]
            xyz = pos.split(",")
            return int(float(xyz[0])), int(float(xyz[1])), int(float(xyz[2]))
        except IndexError:
            logging.error(f"Failed to get info from status {status}")
            return 0, 0, 0

    def home(self) -> tuple[bool, str]:
        self.plotter.timeout = 30
        return self.send("$H", 20)

    def send(self, cmd: str, timeout: int = 10) -> tuple[bool, str]:
        logging.debug(f"sending: {cmd}")
        # self.plotter.timeout = timeout
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

    """
    jogging:
    $J=X10.0 Y-1.5
    """
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('psu_port')
    parser.add_argument('file')
    args = parser.parse_args()

    gcode = open(args.file, 'r').readlines()
    plotter = serial.Serial(args.port, 115200)
    psu = PSU(args.psu_port)

    streamer = GCODEStreamer(plotter, psu)
    streamer.stream(gcode)

    plotter.close()
