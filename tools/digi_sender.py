import time

import serial

port = serial.Serial(
    port="/dev/ttyUSB2", baudrate=1200, parity=serial.PARITY_NONE, timeout=2
)
port.write("/Y,0;K;".encode())
file = open("/home/marcel/dev/cursor/data/experiments/test_sheet/digi/layer1_test_sheet_hp7550a_lt_digiplot_a1_c427b369.digi", "r").readlines()
data = "".join(file)
split_commands = data.split(";")
for cmd in split_commands:
    time.sleep(0.005)
    _cmd = f"{cmd};"
    print(_cmd)
    port.write(_cmd.encode())

#port.write("/Y,27500;K;".encode())