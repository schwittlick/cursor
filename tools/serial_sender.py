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

import wasabi
import serial
from serial import Serial
from time import sleep
import sys

log = wasabi.Printer()


class Discovery:
    def get_machines(self):
        machines = []
        for i in range(9):
            port = f"/dev/ttyUSB{i}"
            try:
                s = Sender(port=port, baud=9600)
                if s.is_open():
                    machines.append((port, s))
            except serial.SerialException:
                continue
        return machines


class Sender:
    def __init__(self, port: str, baud: int):
        self.__feedback = None
        self.__model = None
        self.__serial = Serial(
            port=port, baudrate=baud, parity=serial.PARITY_NONE, timeout=2
        )

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

    def is_open(self):
        return self.__serial.is_open

    def close(self):
        self.__serial.close()

    def model(self) -> str:
        if self.__model is not None:
            return self.__model
        self.__serial.write("OI;\n".encode("utf-8"))
        ret = self.read().decode("utf-8")
        self.__model = ret.strip()
        return self.__model

    def does_feedback(self) -> typing.Tuple[int, bool]:
        if self.__feedback is False:
            return 0, False

        self.__serial.write(b"\x1B.B")
        b = b""
        n = 0

        read_some = False
        attempts = 2
        current_attempt = 0
        while b != b"\r":
            if len(b) > 0:
                read_some = True
                n = n * 10 + b[0] - 48
            b = self.__serial.read()
            current_attempt += 1
            if current_attempt > attempts:
                self.__feedback = False
                return 0, False

        if current_attempt <= attempts:
            self.__feedback = True
        return n, read_some

    def read(self):
        return self.__serial.readline()

    def send(self, data: str):
        pos = 0
        code = data
        self.show_progress(pos, len(code))
        while pos < len(code):
            avail = 512
            if self.__feedback:
                avail, _ = self.does_feedback()
            if avail < 512:
                sleep(0.01)
                continue

            end = pos + avail
            if len(code) - pos < avail:
                end = len(code)

            self.__serial.write(code[pos:end].encode("utf-8"))
            pos = end

            self.show_progress(pos, len(code))


def do_discovery():
    discovery = Discovery()
    machines = discovery.get_machines()
    for port, machine in machines:
        print(f"Found device at port {port}. It's {machine.model()}")
        machine.close()


def do_terminal_input(sender: Sender):
    cmd = input("enter hpgl\n")
    while cmd != "exit":
        sender.send(cmd + "\n\r")
        fb = sender.read()
        print(fb)
        cmd = input("enter hpgl\n")
    else:
        sys.exit(0)


def main():
    parser = ArgumentParser()
    parser.add_argument("--port", required=False)
    parser.add_argument("--baud", required=False, type=int)
    parser.add_argument("--file", required=False)
    parser.add_argument("--discovery", required=False)
    args = parser.parse_args()

    if args.discovery is not None:
        do_discovery()

    if args.port is None or args.baud is None or args.file is None:
        sys.exit()

    sender = Sender(args.port, args.baud)
    data, feedback_success = sender.does_feedback()
    log.good(
        f"plotter at {args.port} ({sender.model()}) w/ "
        f"baud {args.baud} returned {data}, success={feedback_success}"
    )

    if not args.file:
        do_terminal_input(sender)

    with open(args.file, "r") as f:
        code = f.read()
        sender.send(code)


if __name__ == "__main__":
    main()
