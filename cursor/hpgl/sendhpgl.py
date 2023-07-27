from argparse import ArgumentParser
from time import sleep

import wasabi
from serial import Serial, SerialException
from tqdm import tqdm

from cursor.hpgl import ESC_TERM, ESC, ABORT_GRAPHICS, OUTPUT_IDENTIFICATION, WAIT, OUTBUT_BUFFER_SPACE, CR, \
    read_until_char
from cursor.hpgl.tokenize import tokenize

log = wasabi.Printer(pretty=True)


class SerialSender:
    def __init__(self, serialport: str, hpgl_data: str):
        self.serial_port_address = serialport
        self.plotter = Serial(port=serialport, baudrate=9600, timeout=1)
        self.commands = tokenize(hpgl_data)

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

        self.plotter.write(buffer_sizes.encode())
        self.plotter.write(WAIT.encode())

        self.read_until()

        self.plotter.write(logical_buffer_size.encode())
        self.plotter.write(WAIT.encode())
        self.read_until()

    def identify(self):
        self.plotter.write(OUTPUT_IDENTIFICATION.encode())
        answer = self.read_until(self.plotter)
        return answer.split(',')[0]

    def abort(self):
        self.plotter.write(ABORT_GRAPHICS.encode())
        self.plotter.write(WAIT.encode())
        self.read_until()

    def send(self):
        try:
            with tqdm(total=len(self.commands)) as pbar:
                pbar.update(0)
                for cmd in self.commands:
                    self.wait_for_free_io_memory(cmd)
                    self.plotter.write(f"{cmd};".encode('utf-8'))
                    pbar.update(1)
        except KeyboardInterrupt:
            log.warn("Interrupted- aborting.")
            sleep(0.1)
            self.abort()

    def read_until(self, char: chr = CR, timeout: float = 1.0) -> str:
        try:
            return read_until_char(self.plotter, char, timeout)
        except SerialException as se:
            self.plotter.close()
            self.plotter = None
            self.plotter = Serial(port=self.serial_port_address, baudrate=9600, timeout=0.5)
            log.warn("Reconnected serial port..")
            log.warn(f"Because of {se}")

        return ""

    def wait_for_free_io_memory(self, cmd: str) -> None:
        self.plotter.write(OUTBUT_BUFFER_SPACE.encode())
        free_io_memory = int(self.read_until())
        while free_io_memory <= len(cmd):
            sleep(0.1)
            self.plotter.write(OUTBUT_BUFFER_SPACE.encode())
            free_io_memory = int(self.read_until())


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    args = parser.parse_args()

    text = ''.join(open(args.file, 'r', encoding='utf-8').readlines())
    text = text.replace(" ", '').replace("\n", '').replace("\r", '')

    sender = SerialSender(args.port, text)
    sender.send()


if __name__ == '__main__':
    """
    - pause
    - everything in try catch so it can be continued in case of crash
    """
    main()