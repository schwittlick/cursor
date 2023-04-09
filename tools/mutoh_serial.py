import sys
from time import sleep

import serial

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import PlotterType, PaperSize, MinmaxMapping, Paper
from cursor.export import ExportWrapper
from cursor.filter import MaxPointCountFilter, MinPointCountFilter
from cursor.loader import Loader
from cursor.renderer import HPGLRenderer
from tools.octet.discovery import discover


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
    print(f"avail {n}")
    return n


def show_progress(pos, total, length=100):
    fill = length * pos // total
    print('\rProgress: [' + fill * '\u2588' + (length - fill) * '\u2591' + '] ' + str(pos) + ' of ' + str(
        total) + ' bytes sent', end='\r')
    if pos == total:
        print()


def send(serial, code: str):
    pos = 0

    # draftmasters 1024
    # hp 7475 & 7550 512
    # hp 7440 255

    show_progress(pos, len(code))
    while pos < len(code):
        avail = check_avail(serial)
        if avail < 1024:
            sleep(0.01)
            continue

        end = pos + avail
        if len(code) - pos < avail:
            end = len(code)

        serial.write(code[pos:end].encode('utf-8'))
        pos = end

        show_progress(pos, len(code))


def get_data():
    recordings = DataDirHandler().recordings()
    _loader = Loader(directory=recordings, limit_files=4)
    all_paths = _loader.all_paths()

    min_point_filter = MinPointCountFilter(6)
    all_paths.filter(min_point_filter)

    max_point_filter = MaxPointCountFilter(20)
    all_paths.filter(max_point_filter)

    for r in all_paths[:1]:
        pc = Collection()

        r.clean()
        pc.add(r)
        for i in range(1):
            pc.add(pc[0].offset(1 * i))
        for i in range(5):
            pc.add(pc[0].offset(2 * i))
        for i in range(1):
            pc.add(pc[0].offset(1 * (7 - i)))

        for p in pc:
            p.pen_select = 1
            p.velocity = 32

        suffix = f"{r.hash}"

        pc.fit(Paper.sizes[PaperSize.LANDSCAPE_A3], output_bounds=MinmaxMapping.maps[PlotterType.HP_7595A])

        hpgl_renderer = HPGLRenderer(DataDirHandler().hpgl("composition73_mutoh"))
        hpgl_renderer.render(pc)
        data = hpgl_renderer.generate_string()
        return data

        ExportWrapper().ex(
            pc,
            PlotterType.HP_7596B_A3,
            PaperSize.LANDSCAPE_A3,
            30,
            "composition73_mutoh",
            f"{suffix}_small",
        )


if __name__ == "__main__":
    baudrate = 19200
    stopbits = serial.STOPBITS_ONE
    bytesize = serial.SEVENBITS
    parity = serial.PARITY_NONE
    xonxoff = serial.XON
    timeout = 0.1
    result = discover(baudrate=baudrate, stopbits=stopbits, bytesize=bytesize, parity=parity, xonxoff=xonxoff,
                      timeout=timeout)

    if len(result) == 0:
        print("no serial port detected")
        sys.exit(1)
    port = result[0][0]
    model = result[0][1]
    ser = serial.Serial(port=port, baudrate=baudrate, stopbits=stopbits, bytesize=bytesize, parity=parity,
                        xonxoff=xonxoff, timeout=timeout)

    data = get_data()
    print(data)
    send(ser, data)

    # bytes = str.encode(data)
    # ser.write(b'SP1;VS10;PA0,0;PD;PA2000,2000;PA0,2000;PA2000,0;PU;PA0,0;SP0;')
    # ser.write(bytes)
    # ser.flushOutput()
    # ser.close()
