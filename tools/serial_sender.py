# Send HP-GL code to 7475A plotter
# Copyright (C) 2019  Luca Schmid
# Extension to send to all kinda other machines
# Copy right (C) 2022 Marcel Schwittlick

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#  python serial_sender.py /dev/ttyUSB0 1200 0 path/to/fi.le
import typing
from argparse import ArgumentParser
from serial import Serial
from time import sleep


class Sender:
    def __init__(self, port: str, baud: int):
        self.__serial = Serial(port=port, baudrate=baud, timeout=2)

    @staticmethod
    def show_progress(pos, total: int, length: int = 100):
        fill = length * pos // total
        print(
            "\rProgress: ["
            + fill * "\u2588"
            + (length - fill) * "\u2591"
            + "] "
            + str(pos)
            + " of "
            + str(total)
            + " bytes sent",
            end="\r",
        )
        if pos == total:
            print()

    def does_feedback(self) -> typing.Tuple[int, bool]:
        self.__serial.write(b"\x1B.B")
        b = b""
        n = 0

        read_some = False
        while b != b"\r":
            if len(b) > 0:
                read_some = True
                n = n * 10 + b[0] - 48
            b = self.__serial.read()

        return n, read_some

    def send(self, data: str):
        pass


def read_code(path):
    code = ""
    with open(path, "r") as f:
        code = f.read()
    return code


def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument("baud", type=int)
    parser.add_argument("hpgl", type=int)
    parser.add_argument("file")
    args = parser.parse_args()

    sender = Sender(args.port, args.baud)
    feedback = sender.does_feedback()

    print(bool(args.hpgl))
    serial = Serial(port=args.port, baudrate=args.baud, timeout=0)
    code = read_code(args.file)
    pos = 0

    Sender.show_progress(pos, len(code))
    while pos < len(code):
        avail = 512
        if feedback:
            avail, success = sender.does_feedback()
        if avail < 512:
            sleep(0.01)
            continue

        end = pos + avail
        if len(code) - pos < avail:
            end = len(code)

        serial.write(code[pos:end].encode("utf-8"))
        pos = end

        Sender.show_progress(pos, len(code))


if __name__ == "__main__":
    main()
