import logging
import time

from serial import Serial, SerialException

from cursor.hpgl import read_until_char, CR, OUTPUT_IDENTIFICATION, WAIT, ABORT_GRAPHICS, OUTBUT_BUFFER_SPACE, \
    OUTPUT_POSITION
from cursor.hpgl.plotter.memory_config import HP7550AMemoryConfig, DraftMasterMemoryConfig
from cursor.position import Position


class HPGLPlotter:
    def __init__(self, serialport: Serial):
        self.serial = serialport

        model = self.identify()
        logging.info(f"Detected model {model}")
        if model == "7550A":
            dm = HP7550AMemoryConfig()
            memory_config, plotter_config = dm.memory_alloc_cmd(12752, 4, 0, 0, 44)
            logging.info(f"Applying custom config to {model}")
            logging.info(memory_config)
            logging.info(plotter_config)
            self.apply_config(memory_config, plotter_config)
        if model in ["7595A", "7596A"]:
            dm = DraftMasterMemoryConfig()
            memory_config, plotter_config = dm.memory_alloc_cmd(25518, 4, 0, 66, 12)
            logging.info(f"Applying custom config to {model}")
            logging.info(memory_config)
            logging.info(plotter_config)
            self.apply_config(memory_config, plotter_config)

    def write(self, data):
        self.serial.write(data.encode())

    def abort(self):
        self.write(ABORT_GRAPHICS)
        self.write(WAIT)
        self.read_until()

    def identify(self):
        self.write(OUTPUT_IDENTIFICATION)
        answer = self.read_until()
        return answer.split(',')[0]

    def free_memory(self):
        self.write(OUTBUT_BUFFER_SPACE)
        free_memory = self.read_until()
        logging.info(f"free memory: {free_memory}")
        try:
            free_io_memory = int(free_memory)
        except ValueError as ve:
            logging.warning(f"Failed getting info from plotter: {ve}")
            free_io_memory = 0

        return free_io_memory

    def get_position(self) -> Position:
        self.write(OUTPUT_POSITION)
        answer = self.read_until()
        # logging.info(answer)
        if len(answer) == 0:
            return Position(0, 0)
        current_pos = answer.split(',')
        if len(current_pos) < 2:
            # should throw an exception and handle at caller
            return Position()
        return Position(int(current_pos[0]), int(current_pos[1]))

    def reopen(self):
        self.serial.close()
        time.sleep(0.5)
        self.serial.open()

    def read_until(self, char: chr = CR, timeout: float = 1.0) -> str:
        try:
            return read_until_char(self.serial, char, timeout)
        except SerialException as se:
            self.reopen()
            logging.warning("Reconnected serial port..")
            logging.warning(f"Because of {se}")

        return ""

    def apply_config(self, memory_config: str, plotter_config: str):
        self.write(memory_config)
        self.write(WAIT)

        self.read_until()

        self.write(plotter_config)
        self.write(WAIT)
        self.read_until()
