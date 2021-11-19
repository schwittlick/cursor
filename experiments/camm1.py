from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter

import math
import serial



if __name__ == "__main__":
    with serial.Serial('COM3', 9600, timeout=1) as ser:
        dontwork = f"{chr(27)}.B"
        init = f"{chr(27)}IN;\n\r"
        bytes = str.encode(init)
        ser.write(bytes)
