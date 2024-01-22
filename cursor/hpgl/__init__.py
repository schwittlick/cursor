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
ABORT_GRAPHICS = f"{ESC}.K"  # clears partially parsed cmds and clears buffer
WAIT = f"{ESC}.L"  # returns io buffer size when its empty. read it and wait for reply before next command
OUTPUT_DIMENSIONS = "OH;"
OUTPUT_POSITION = "OA;"


def read_until_char(port: serial.Serial, char: chr = CR, timeout: float = 1.0):
    timer = Timer()
    data = ""
    while timer.elapsed() < timeout:
        by = port.read()
        if by.decode() != char:
            data += by.decode()
        else:
            # logging.info(f"read_until_char took {timer.elapsed()}")
            return data
    return data
