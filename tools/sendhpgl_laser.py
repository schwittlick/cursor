# Send HP-GL code to 7475A plotter
# Copyright (C) 2019  Luca Schmid
# Copyright (C) 2022  Marcel Schwittlick

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

from argparse import ArgumentParser
from time import sleep

from serial import Serial


def read_code(path):
    code = 'IN;'
    with open(path, 'r') as f:
        code = f.read()
    return code


def check_avail(serial):
    serial.write(b'\x1B.B')
    b = b''
    n = 0
    while b != b'\r':
        if len(b) > 0:
            n = n * 10 + b[0] - 48
        b = serial.read()
    # print(f"avail {n}")
    return n


def show_progress(pos, total, length=100):
    fill = length * pos // total
    print('\rProgress: [' + fill * '\u2588' + (length - fill) * '\u2591' + '] ' + str(pos) + ' of ' + str(
        total) + ' bytes sent', end='\r')
    if pos == total:
        print()


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    parser.add_argument('arduino_port')
    args = parser.parse_args()

    serial = Serial(port=args.port, timeout=0)
    serial_arduino = Serial(port=args.arduino_port, timeout=0)

    code = read_code(args.file)
    pos = 0

    # hp 7475, draftmasters 1024
    # hp 7475 & 7550 512
    # hp 7440 255

    BUFFER_SIZE = 512
    LASER_ON = "10"
    LASER_OFF = "0"

    show_progress(pos, len(code))
    while pos < len(code):
        avail = check_avail(serial)
        if avail < BUFFER_SIZE:
            sleep(0.01)
            continue

        end = pos + avail
        if len(code) - pos < avail:
            end = len(code)

        snip = code[pos:end]
        snip = snip.replace("\n", "")
        commands = snip.split(";")
        for c in commands:
            if c == "PD":
                serial_arduino.write(LASER_ON.encode('utf-8'))
                continue
            if c == "PU":
                serial_arduino.write(LASER_OFF.encode('utf-8'))
                continue
            if c.startswith("SP"):
                continue
            serial.write(c.encode('utf-8'))
        pos = end

        show_progress(pos, len(code))


if __name__ == '__main__':
    main()
