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

import wasabi
from serial import Serial, SerialException
from tqdm import tqdm

from cursor.hpgl.tokenize import tokenize
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


class SerialSender:
    def __init__(self, serialport: str, hpgl_file: str):
        self.serial_port_address = serialport
        self.port = Serial(port=serialport, baudrate=9600, timeout=0.5)
        self.commands = tokenize(open(hpgl_file, 'r').read())

        model = self.identify()
        log.info(f"Detected model {model}")
        if model == "7550A":
            self.config_memory(12752, 4, 0, 0, 44)

    def config_memory(self, io: int = 1024, polygon: int = 1778, char: int = 0, replot: int = 9954,
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

        self.port.write(buffer_sizes.encode())
        self.port.write(WAIT.encode())

        self.read_until()

        self.port.write(logical_buffer_size.encode())
        self.port.write(WAIT.encode())
        self.read_until()

    def identify(self):
        self.port.write(OUTPUT_IDENTIFICATION.encode())
        answer = self.read_until(self.port)
        return answer.split(',')[0]

    def abort(self):
        self.port.write(ABORT_GRAPHICS.encode())
        self.port.write(WAIT.encode())
        self.read_until()

    def send(self):
        try:
            with tqdm(total=len(self.commands)) as pbar:
                pbar.update(0)
                for cmd in self.commands:
                    self.wait_for_free_io_memory(cmd)
                    self.port.write(cmd.encode('utf-8'))
                    pbar.update(1)
        except KeyboardInterrupt:
            log.warn(f"Interrupted- aborting.")
            sleep(0.1)
            self.abort()

    def read_until(self, char: chr = CR, timeout: float = 1.0):
        timer = Timer()
        data = ""
        while timer.elapsed() < timeout:
            try:
                by = self.port.read().decode()
                if by != char:
                    data += by
                else:
                    return data
            except SerialException as se:
                self.port.close()
                self.port = None
                self.port = Serial(port=self.serial_port_address, baudrate=9600, timeout=0.5)
                log.warn("Reconnected serial port..")
                log.warn(f"Because of {se}")

        return data

    def wait_for_free_io_memory(self, cmd: str) -> None:
        self.port.write(OUTBUT_BUFFER_SPACE.encode())
        free_io_memory = int(self.read_until())
        while free_io_memory <= len(cmd):
            sleep(0.1)
            self.port.write(OUTBUT_BUFFER_SPACE.encode())
            free_io_memory = int(self.read_until())


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    args = parser.parse_args()

    sender = SerialSender(args.port, args.file)
    sender.send()


if __name__ == '__main__':
    """
    - pause
    - everything in try catch so it can be continued in case of crash
    """
    main()
