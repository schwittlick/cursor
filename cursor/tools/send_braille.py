import logging
import pathlib
from tkinter import filedialog
import tkinter as tk

import serial

if __name__ == "__main__":
    port = "/dev/ttyUSB3"
    baud = 9600
    response = ""
    s = serial.Serial(
        port,
        baud,
        timeout=1,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=True
    )

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    path = pathlib.Path(file_path)

    logging.info(f"Loaded {path.as_posix()}")

    with open(path.as_posix(), "r") as vim:
        lines = vim.readlines()
        for line in lines:
            logging.info(line)
            s.write(line.encode())
