import logging

import serial

from cursor.timer import Timer

ESC = chr(27)
CR = chr(13)
LF = chr(10)
LB_TERMINATOR = chr(3)
ESC_TERM = ":"
OUTBUT_BUFFER_SPACE = f"{ESC}.B"
OUTPUT_EXTENDED_STATUS = f"{ESC}.O"  # info about device satus etc
OUTPUT_IDENTIFICATION = f"{ESC}.A"  # immediate return e.g. "7550A,firmwarenr"
MODEL_IDENTIFICATION = "OI;"  # immediate return e.g. "7470A"
ABORT_GRAPHICS = f"{ESC}.K"  # clears partially parsed cmds and clears buffer
RESET_DEVICE = f"{ESC}.R"  # This command sets all the settings of the device control commands to their default values.
WAIT = f"{ESC}.L"  # returns io buffer size when its empty. read it and wait for reply before next command
OUTPUT_DIMENSIONS = "OH;"
OUTPUT_POSITION = "OA;"


def read_until_char(port: serial.Serial, char: chr = CR, timeout: float = 1.0) -> str:
    timer = Timer()
    data = ""
    while timer.elapsed() < timeout:
        by = port.read()
        try:
            if by.decode() != char:
                data += by.decode()
            else:
                # logging.info(f"read_until_char took {timer.elapsed()}")
                return data
        except UnicodeDecodeError as ude:
            logging.warning(port)
            logging.warning(ude)
            logging.warning(f"Couldn't decode {by}. Skipping and returning empty string")
            return ""
    return data
