# Send HP-GL code to 7475A plotter
# Copyright (C) 2019  Luca Schmid
# Copyright (C) 2022  Marcel Schwittlick
import time
import typing
from argparse import ArgumentParser
from time import sleep

import serial
import wasabi
from serial import Serial

log = wasabi.Printer()

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

    serial = Serial(port=args.port, timeout=100)
    serial_arduino = Serial(port=args.arduino_port, timeout=100)

    code = read_code(args.file)

    LASER_ON = "10"
    LASER_OFF = "0"

    snip = code.replace("\n", "")
    commands = snip.split(";")
    current = "PD"
    for c in commands:
        if c == "PD":
            serial_arduino.write(LASER_ON.encode('utf-8'))
            ret = serial_arduino.read_all()
            print(f"received {ret}")
            current = c
        if c == "PU":
            serial_arduino.write(LASER_OFF.encode('utf-8'))
            ret = serial_arduino.read_all()
            print(f"received {ret}")
            current = c
        if c.startswith("SP"):
            pass
        if c.startswith('PA'):

            pos = c[2:].split(',')
            po = (int(pos[0]), int(pos[1]))
            serial.write(f"{c};".encode('utf-8'))

            if current == 'PU':
                # sleep because it already
                # reports back that it arrived
                time.sleep(1.0)

            succ = poll(serial, po)
            log.info(f'poll: {succ}')
        if c.startswith('VS') or c.startswith('LT'):
            serial.write(f"{c};".encode('utf-8'))


def readit(port):
    response = ''
    while True:
        response += port.read().decode()
        if '\r' in response:
            return response

def poll(ser: serial.Serial, target_pos: typing.Tuple):
    ser.write('OA;'.encode('utf-8'))
    ret = readit(ser).rstrip()
    if len(ret) == 0:
        return False
    current_pos = ret.split(',')
    current_po = (int(current_pos[0]), int(current_pos[1]))

    attempts = 0
    while current_po != target_pos:
        ser.write('OA;'.encode('utf-8'))
        ret = readit(ser).rstrip()
        if len(ret) == 0:
            attempts += 1
            continue

        if ',' not in ret:
            attempts += 1
            continue

        current_pos = ret.split(',')
        current_po = (int(current_pos[0]), int(current_pos[1]))


        time.sleep(0.1)

        if attempts > 10:
            return False
    return True


if __name__ == '__main__':
    main()
