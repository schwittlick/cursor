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
from serial import Serial
from time import sleep

ESC = chr(27)
OUTBUT_BUFFER_SPACE = f"{ESC}.B".encode()
OUTPUT_EXTENDED_STATUS = f"{ESC}.O".encode()  # info about device satus etc
OUTPUT_IDENTIFICATION = f"{ESC}.A"  # immediate return e.g. "7550A,firmwarenr"
ABORT_GRAPHICS = f"{ESC}.K"  # clears partially parsed cmds and clears buffer


def check_avail(serial):
    serial.write(OUTBUT_BUFFER_SPACE)
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
    args = parser.parse_args()

    serial = Serial(port=args.port, timeout=0)

    code = open(args.file, 'r').read()
    pos = 0

    # draftmasters 1024
    # hp 7475 & 7550 512
    # hp 7440 255

    BUFFER_SIZE = 512

    show_progress(pos, len(code))
    while pos < len(code):
        avail = check_avail(serial)
        if avail < BUFFER_SIZE:
            sleep(0.01)
            continue

        end = pos + avail
        if len(code) - pos < avail:
            end = len(code)

        serial.write(code[pos:end].encode('utf-8'))
        pos = end

        show_progress(pos, len(code))


if __name__ == '__main__':
    main()
