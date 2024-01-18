import logging
from argparse import ArgumentParser
from time import sleep

from serial import Serial, SerialException
from tqdm import tqdm

from cursor.hpgl import ESC, CR, LB_TERMINATOR, ESC_TERM, OUTBUT_BUFFER_SPACE, OUTPUT_IDENTIFICATION, ABORT_GRAPHICS, \
    WAIT, read_until_char
from cursor.hpgl.analyze import HPGLAnalyzer
from cursor.hpgl.hpgl_tokenize import tokenizer


class DraftMasterMemoryConfig:
    def __init__(self):
        self.physical_io_buffer = 2, 25518
        self.polygon_buffer = 4, 25520
        self.char_buffer = 0, 25516
        self.vector_buffer = 66, 25582
        self.pen_sort_buffer = 12, 24528

        self.max_sum = 25600

    def memory_alloc_cmd(self, io: int = 1024, polygon: int = 3072, char: int = 0, vector: int = 3000,
                         pen_sort: int = 18504) -> tuple[str, str]:
        assert self.physical_io_buffer[0] <= io <= self.physical_io_buffer[1]
        assert self.polygon_buffer[0] <= polygon <= self.polygon_buffer[1]
        assert self.char_buffer[0] <= char <= self.char_buffer[1]
        assert self.vector_buffer[0] <= vector <= self.vector_buffer[1]
        assert self.pen_sort_buffer[0] <= pen_sort <= self.pen_sort_buffer[1]
        assert sum([io, polygon, char, vector, pen_sort]) <= self.max_sum

        memory_config = f"{ESC}.T{io};{polygon};{char};{vector};{pen_sort}{ESC_TERM}"

        io_conditions = 3
        # io_conditions specifies an integer equivalent value that controls the states of bits 0 through 4
        # of the configuration byte. When using an RS-232-C interface, these bits control hardware handshake,
        # communications protocol, monitor modes 1 and 2, and block I/O error checking. When using HP-IB
        # interface, this parameter is ignored.
        # Check chapter 15-28 Device-Control Instructions of HP Draftmaster Programmers Reference
        plotter_config = f"{ESC}.@{io};{io_conditions}{ESC_TERM}"

        return memory_config, plotter_config


class HP7550AMemoryConfig:
    def __init__(self):
        self.physical_io_buffer = 2, 12752
        self.polygon_buffer = 4, 12754
        self.char_buffer = 0, 12750
        self.replot_buffer = 0, 12750
        self.vector_buffer = 44, 12794

        self.max_sum = 12800

    def memory_alloc_cmd(self, io: int = 1024, polygon: int = 1778, char: int = 0, replot: int = 9954,
                         vector: int = 44) -> tuple[str, str]:
        assert self.physical_io_buffer[0] <= io <= self.physical_io_buffer[1]
        assert self.polygon_buffer[0] <= polygon <= self.polygon_buffer[1]
        assert self.char_buffer[0] <= char <= self.char_buffer[1]
        assert self.replot_buffer[0] <= replot <= self.replot_buffer[1]
        assert self.vector_buffer[0] <= vector <= self.vector_buffer[1]
        assert sum([io, polygon, char, replot, vector]) <= self.max_sum

        buffer_sizes = f"{ESC}.T{io};{polygon};{char};{replot};{vector}{ESC_TERM}"
        logical_buffer_size = f"{ESC}.@{io}{ESC_TERM}"

        return buffer_sizes, logical_buffer_size


class SerialSender:
    def __init__(self, serialport: str, hpgl_data: str):
        self.serial_port_address = serialport
        self.commands = tokenizer(hpgl_data)

        self.plotter = Serial(port=serialport, baudrate=9600, timeout=1)

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

    def apply_config(self, memory_config: str, plotter_config: str):
        self.plotter.write(memory_config.encode())

        self.plotter.write(WAIT.encode())

        self.read_until()

        self.plotter.write(plotter_config.encode())
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

    def concat_commands(self, cmd_list: list[str]) -> str:
        concatenated = ''
        for cmd in cmd_list:
            if cmd.startswith("LB"):
                concatenated += f"{cmd}{LB_TERMINATOR}"
            else:
                concatenated += f"{cmd};"
        return concatenated

    def send(self):
        command_batch = 20
        # the amount of commands that are being sent to the plotter
        # in one batch. this speeds up drawing. take care to not send too
        # long commands that exceed the maximum buffer size
        logging.info(f"Sending with batch_count: {command_batch}")
        try:
            with tqdm(total=len(self.commands)) as pbar:
                pbar.update(0)
                for i in range(0, len(self.commands), command_batch):
                    batched_commands = self.commands[i:i + command_batch]
                    cmds = self.concat_commands(batched_commands)
                    self.wait_for_free_io_memory(len(cmds) + 10)

                    self.plotter.write(cmds.encode('utf-8'))
                    pbar.update(command_batch)
        except KeyboardInterrupt:
            logging.warning("Interrupted- aborting.")

            sleep(0.1)
            self.abort()

    def read_until(self, char: chr = CR, timeout: float = 1.0) -> str:
        try:
            return read_until_char(self.plotter, char, timeout)
        except SerialException as se:
            self.plotter.close()
            self.plotter = None
            self.plotter = Serial(port=self.serial_port_address, baudrate=9600, timeout=0.5)
            logging.warning("Reconnected serial port..")
            logging.warning(f"Because of {se}")

        return ""

    def wait_for_free_io_memory(self, memory_amount: int) -> None:
        self.plotter.write(OUTBUT_BUFFER_SPACE.encode())
        free_memory = self.read_until()
        try:
            free_io_memory = int(free_memory)
        except ValueError as ve:
            logging.warning(f"Failed getting info from plotter: {ve}")
            free_io_memory = 0

        while free_io_memory < memory_amount:
            sleep(0.05)
            self.plotter.write(OUTBUT_BUFFER_SPACE.encode())
            # logging.info(f"Waiting for free memory..")
            try:
                free_io_memory = int(self.read_until())
            except ValueError as ve:
                logging.warning(f"Failed getting info from plotter: {ve}")
                free_io_memory = 0


def main():
    parser = ArgumentParser()
    parser.add_argument('port')
    parser.add_argument('file')
    args = parser.parse_args()

    analyzer = HPGLAnalyzer()
    analyzer.analyze(args.file)

    text = ''.join(open(args.file, 'r', encoding='utf-8').readlines())
    # text = text.replace(" ", '').replace("\n", '').replace("\r", '')

    sender = SerialSender(args.port, text)
    sender.send()


if __name__ == '__main__':
    test_filename = "/home/marcel/introspection/hwf.txt.hpgl.hpgl.hpgl"
    test_serialport = "/dev/ttyUSB1"
    text = ''.join(open(test_filename, 'r', encoding='utf-8').readlines())
    # text = text.replace(" ", '').replace("\n", '').replace("\r", '')

    sender = SerialSender(test_serialport, text)
    sender.send()
