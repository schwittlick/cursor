# Send HP-GL code to a plotter
# Copyright (C) 2023  Marcel Schwittlick

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

import serial
import wasabi
from serial import Serial
from tqdm import tqdm

from cursor.timer import Timer

log = wasabi.Printer(pretty=True)

ESC = chr(27)
CR = chr(13)
LF = chr(10)
ESC_TERM = ":"

OUTBUT_BUFFER_SPACE = f"{ESC}.B"
OUTPUT_EXTENDED_STATUS = f"{ESC}.O"  # info about device satus etc
OUTPUT_IDENTIFICATION = f"{ESC}.A"  # immediate return e.g. "7550A,firmwarenr"
ABORT_GRAPHICS = f"{ESC}.K"  # clears partially parsed cmds and clears buffer
WAIT = f"{ESC}.L"  # returns io buffer size when its empty. read it and wait for reply before next command


def read_until(port: serial.Serial, char: chr = CR, timeout: float = 1.0):
    timer = Timer()
    data = ""
    while timer.elapsed() < timeout:
        by = port.read().decode()
        if by != char:
            data += by
        else:
            return data
    return data


def config_memory(serial: serial.Serial, io: int = 1024, polygon: int = 1778, char: int = 0, replot: int = 9954,
                  vector: int = 44):
    max_memory_hp7550 = 12800

    assert 2 <= io <= 12752
    assert 4 <= polygon <= 12754
    assert 0 <= char <= 12750
    assert 0 <= replot <= 12750
    assert 44 <= vector <= 12794
    assert sum([io, polygon, char, replot, vector]) <= max_memory_hp7550

    buffer_sizes = f"{ESC}.T{io};{polygon};{char};{replot};{vector}{ESC_TERM}"
    logical_buffer_size = f"{ESC}.@{io}{ESC_TERM}"

    serial.write(buffer_sizes.encode())
    serial.write(WAIT.encode())

    read_until(serial)

    serial.write(logical_buffer_size.encode())
    serial.write(WAIT.encode())
    read_until(serial)


def identify(port: serial.Serial):
    port.write(OUTPUT_IDENTIFICATION.encode())
    answer = read_until(port)
    return answer.split(',')[0]


def abort(port: serial.Serial):
    port.write(ABORT_GRAPHICS.encode())
    port.write(WAIT.encode())
    read_until(port)


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    args = parser.parse_args()

    port = Serial(port=args.port, baudrate=9600, timeout=0.5)

    code = open(args.file, 'r').read()
    pos = 0

    BATCH_SIZE = 128
    model = identify(port)
    log.info(f"Detected model {model}")
    if model == "7550A":
        config_memory(port, 12752, 4, 0, 0, 44)
    try:
        with tqdm(total=len(code)) as pbar:
            pbar.update(0)

            while pos < len(code):
                port.write(OUTBUT_BUFFER_SPACE.encode())
                free_io_memory = int(read_until(port))
                if free_io_memory < BATCH_SIZE:
                    sleep(0.01)
                    continue

                end = pos + BATCH_SIZE
                if len(code) - pos < BATCH_SIZE:
                    end = len(code)
                port.write(code[pos:end].encode('utf-8'))
                pbar.update(BATCH_SIZE)

                pos = end
    except KeyboardInterrupt:
        log.warn(f"Interrupted- aborting.")
        sleep(0.1)
        abort(port)


if __name__ == '__main__':
    main()
