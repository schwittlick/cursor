import logging
import threading
import time
import typing
from time import sleep

import serial
from tqdm import tqdm

from cursor.hpgl import read_until_char, LB_TERMINATOR
from cursor.hpgl.plotter.plotter import HPGLPlotter


def send_and_receive(serial_connection: serial.Serial, command: str, timeout: float = 1.0) -> str | None:
    """
    Wrapper function to wait for an answer from a serial port.

    Works with most plotters, once the communication works, it will return a CR after an answer.
    """
    try:
        serial_connection.write(command.encode())
        logging.debug(f"{serial_connection.port} <- {command}")
        received_data = read_until_char(serial_connection, timeout=timeout)
        logging.debug(f"{serial_connection.port} -> {received_data}")
        if len(received_data) > 0:
            return received_data
    except serial.SerialException as e:
        logging.error(f"Error: {str(e)}")

    return None


def concat_commands(cmd_list: list[str]) -> str:
    concatenated = ''
    for cmd in cmd_list:
        if cmd.startswith("LB"):
            concatenated += f"{cmd}{LB_TERMINATOR}"
        else:
            concatenated += f"{cmd};"
    return concatenated


def wait_for_free_io_memory(plotter: HPGLPlotter, memory_amount: int) -> None:
    free_io_memory = plotter.free_memory()

    logging.info(f"Free memory: {free_io_memory}")

    while free_io_memory < memory_amount:
        sleep(0.05)
        free_io_memory = plotter.free_memory()


class AsyncSerialSender(threading.Thread):
    def __init__(self, plotter: HPGLPlotter):
        super().__init__()

        # these parameters are set when commands are added to the sender
        self.commands = []
        self.command_batch = 1
        self.progress_cb = None

        # default init
        self.plotter = plotter
        self.paused = False
        self.stopped = False
        self.abort_queue = False
        self.send_single = False

        self.do_software_handshake = True

        self.lock = threading.Lock()
        self.current_command_index = 0

    def add_commands(self, commands: list[str], progress_cb: typing.Callable):
        with self.lock:
            self.commands = commands
            self.command_batch = min(20, len(commands))
            self.progress_cb = progress_cb
            self.current_command_index = 0

        logging.info(f"Added {len(commands)} to async sender. batch: {self.command_batch}")

    def insert_commands(self, commands: list[str]):
        with self.lock:
            # Insert the new commands at the current position
            logging.info(f"Inserting {len(commands)} into async sender at index: {self.current_command_index}")
            self.commands[self.current_command_index:self.current_command_index] = commands

    def run(self):
        while not self.stopped:
            while self.current_command_index < len(self.commands):
                if self.abort_queue:
                    self.plotter.abort()
                    self.commands = []
                    self.current_command_index = 0
                    self.abort_queue = False
                    logging.info("Stopped AsyncSerialSender")
                    break

                end_index = min(self.current_command_index + self.command_batch, len(self.commands))
                with self.lock:
                    logging.info(f"Getting commands from index: {self.current_command_index}, end: {end_index}")
                    batched_commands = self.commands[self.current_command_index:end_index]
                cmds = concat_commands(batched_commands)

                if self.do_software_handshake:
                    wait_for_free_io_memory(self.plotter, len(cmds) + 10)

                logging.info(cmds)
                self.plotter.write(cmds)

                while self.paused:
                    #self.lock.release()
                    time.sleep(0.1)
                    #self.lock.acquire()

                if self.send_single and not self.paused:
                    self.command_batch = 1
                    self.paused = True

                self.current_command_index = end_index
                #self.lock.release()
                time.sleep(0.1)
                #self.lock.acquire()

                # call cb for progress
                self.progress_cb(self.current_command_index)

            # after the currently set commands are done
            # empty the queue and reset the index
            self.commands = []
            self.current_command_index = 0

            # wait until new commands have been set
            time.sleep(1)


class SerialSender:
    def __init__(self):
        pass
        # parser = HPGLParser()
        # collection = parser.parse(hpgl_data)
        # collection.sort(Sorter(param=SortParameter.PEN_SELECT, reverse=False))
        # now the problem is the scaling, we don't know the export parameters
        # self.commands = tokenizer(hpgl_data)
        # self.plotter = HPGLPlotter(serialport)

    @staticmethod
    def send(plotter: HPGLPlotter, commands: list[str]):
        command_batch = 20
        # the amount of commands that are being sent to the plotter
        # in one batch. this speeds up drawing. take care to not send too
        # long commands that exceed the maximum buffer size
        logging.info(f"Sending with batch_count: {command_batch}")
        try:
            with tqdm(total=len(commands)) as pbar:
                pbar.update(0)
                for i in range(0, len(commands), command_batch):
                    batched_commands = commands[i:i + command_batch]
                    cmds = concat_commands(batched_commands)
                    wait_for_free_io_memory(plotter, len(cmds) + 10)

                    plotter.write(cmds)
                    pbar.update(command_batch)
        except KeyboardInterrupt:
            logging.warning("Interrupted- aborting.")

            sleep(0.1)
            plotter.abort()
