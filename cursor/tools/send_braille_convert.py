import logging
import sys
import tkinter as tk
import pathlib
from argparse import ArgumentParser
from tkinter import filedialog

import serial

from cursor.tools.braille_converter import convert


def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(initialdir='/home/marcel/braille/')

    if not file_path:
        logging.warning("Not selected any file. Aborting")
        sys.exit(0)

    path = pathlib.Path(file_path)

    vim_data = convert(path)

    parser = ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()

    baud = 9600
    s = serial.Serial(
        args.port,
        baud,
        timeout=1,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=True,
    )

    for line in vim_data:
        logging.info(line)
        s.write(line.encode())

    logging.info(f"Finished sending to {s.port}")


if __name__ == "__main__":
    main()
