import logging
import pathlib
from argparse import ArgumentParser
from tkinter import filedialog
import tkinter as tk

import serial

if __name__ == "__main__":
    """
    There is no way to "detect" a Index Everest V2.
    It does not respond on any input..
    """

    parser = ArgumentParser()
    parser.add_argument('port')
    args = parser.parse_args()

    baud = 9600
    response = ""
    s = serial.Serial(
        args.port,
        baud,
        timeout=1,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=True,
    )

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(initialdir='/home/marcel/braille/')
    path = pathlib.Path(file_path)

    logging.info(f"Loaded {path.as_posix()}")

    with open(path.as_posix(), "r") as vim:
        lines = vim.readlines()
        for line in lines:
            logging.info(line)
            s.write(line.encode())
