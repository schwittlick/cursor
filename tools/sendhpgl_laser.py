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

# Send HP-GL code to hpgl plotters
# Copyright (C) 2019  Luca Schmid
# Copyright (C) 2022  Marcel Schwittlick
import re
import time
import typing
from argparse import ArgumentParser

import serial
import wasabi
from serial import Serial

log = wasabi.Printer()

DEBUG = True


def read_code(path):
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


def set_arduino_pwm(arduino: serial.Serial, pwm: int):
    log.info(f"set arduino pwm: {pwm}")
    arduino.write(f"{pwm}".encode('utf-8'))
    ret = arduino.read_all()
    log.info(f"arduino: {ret}")


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    parser.add_argument('arduino_port')
    args = parser.parse_args()

    serial = Serial(port=args.port, timeout=50)
    serial_arduino = Serial(port=args.arduino_port, timeout=50)
    serial_arduino.flush()

    code = read_code(args.file)

    LASER_OFF = 0

    snip = code.replace("\n", "")
    commands = snip.split(";")
    current = "PU"
    current_pwm = 0
    last_pos = (0, 0)
    for c in commands:
        if c == "PD":
            set_arduino_pwm(serial_arduino, current_pwm)
            current = c
            serial.write(f"{c};".encode('utf-8'))
        if c == "PU":
            if current == 'PA':
                little_off = (last_pos[0] + 1, last_pos[1])
                send_and_wait(serial, c, little_off)
                pass
            set_arduino_pwm(serial_arduino, LASER_OFF)
            current = c
            # no need to do pen up
            # serial.write(f"{c};".encode('utf-8'))
        if c.startswith("SP"):
            # ignore pen select
            pass
        if c.startswith('PA'):
            if DEBUG:
                log.info(f"{c}")

            po = parse_pa(c)
            send_and_wait(serial, c, po)
            last_pos = po

            current = 'PA'
        if c.startswith('PWM'):
            parsed_pwm = int(re.findall(r'\d+', c)[0])
            current_pwm = parsed_pwm
            log.info(f"current_pwm: {parsed_pwm}")
        if c.startswith('VS'):
            log.info(f"{c}")
            serial.write(f"{c};".encode('utf-8'))


def parse_pa(c):
    pos = c[2:].split(',')
    po = (int(pos[0]), int(pos[1]))
    return po


def send_and_wait(plotter, cmd, position):
    plotter.write(f"PA{position[0]},{position[1]};".encode('utf-8'))
    poll(plotter, position)


def readit(port):
    response = ''
    while True:
        response += port.read().decode()
        if '\r' in response:
            return response


def poll(ser: serial.Serial, target_pos: typing.Tuple):
    if DEBUG:
        return True

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

        if attempts > 20:
            return False
    return True


if __name__ == '__main__':
    main()
