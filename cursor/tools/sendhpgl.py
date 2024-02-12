import logging
from argparse import ArgumentParser
from time import sleep

from tqdm import tqdm

from cursor.hpgl import LB_TERMINATOR
from cursor.hpgl.analyze import HPGLAnalyzer
from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.plotter.plotter import HPGLPlotter


def concat_commands(cmd_list: list[str]) -> str:
    concatenated = ''
    for cmd in cmd_list:
        if cmd.startswith("LB"):
            concatenated += f"{cmd}{LB_TERMINATOR}"
        else:
            concatenated += f"{cmd};"
    return concatenated


class SerialSender:
    def __init__(self, serialport: str, hpgl_data: str):
        # parser = HPGLParser()
        # collection = parser.parse(hpgl_data)
        # collection.sort(Sorter(param=SortParameter.PEN_SELECT, reverse=False))
        # now the problem is the scaling, we don't know the export parameters
        self.commands = tokenizer(hpgl_data)
        self.plotter = HPGLPlotter(serialport)

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
                    cmds = concat_commands(batched_commands)
                    self.wait_for_free_io_memory(len(cmds) + 10)

                    self.plotter.write(cmds)
                    pbar.update(command_batch)
        except KeyboardInterrupt:
            logging.warning("Interrupted- aborting.")

            sleep(0.1)
            self.plotter.abort()

    def wait_for_free_io_memory(self, memory_amount: int) -> None:
        free_io_memory = self.plotter.free_memory()

        while free_io_memory < memory_amount:
            sleep(0.05)
            free_io_memory = self.plotter.free_memory()


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
