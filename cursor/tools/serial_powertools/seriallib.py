import logging
import threading
import time
import typing
from time import sleep

import serial
from tqdm import tqdm

from cursor.hpgl import LB_TERMINATOR, read_until_char
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
    concatenated = ""
    for cmd in cmd_list:
        if cmd.startswith("LB"):
            concatenated += f"{cmd}{LB_TERMINATOR}"
        else:
            concatenated += f"{cmd};"
    return concatenated


MODAL = set("IN DF AP SP VS FS AS LT PT CT CV GM GP SG IP SC IW RO DI DR SI SR SL LO ES DT CS CA SS SA".split())


def _mnemonic(command: str) -> str:
    return command[:2].upper()


def state_before(commands: list[str], index: int) -> list[str]:
    """
    The modal instructions a plotter would be carrying at `index` had the file
    been sent from the start: the last IN and, after it, the last occurrence of
    every mode-setting mnemonic, in file order. Replayed before resuming
    part-way through a file so pen, speed, force, line type and the like match.
    """
    start = next((i for i in range(index - 1, -1, -1) if _mnemonic(commands[i]) == "IN"), 0)
    latest: dict[str, int] = {}
    for i in range(start, index):
        if _mnemonic(commands[i]) in MODAL:
            latest[_mnemonic(commands[i])] = i
    return [commands[i] for i in sorted(latest.values())]


def resume_point(commands: list[str], index: int) -> int:
    """The first pen-up at or after index, so a resumed plot never draws from wherever the pen happens to be."""
    return next((i for i in range(index, len(commands)) if _mnemonic(commands[i]) == "PU"), index)


def wait_for_free_io_memory(plotter: HPGLPlotter, memory_amount: int, limit: int = 64) -> None:
    free_io_memory = plotter.free_memory()
    free_io_memory = min(free_io_memory, limit)

    logging.info(f"Free memory: {free_io_memory} requested: {memory_amount}")

    while free_io_memory < memory_amount:
        sleep(0.05)
        free_io_memory = plotter.free_memory()
        free_io_memory = min(free_io_memory, limit)
        logging.info(f"Free memory: {free_io_memory} requested: {memory_amount}")


class AsyncSerialSender(threading.Thread):
    def __init__(self, plotter: HPGLPlotter):
        super().__init__()

        # these parameters are set when commands are added to the sender
        self.commands = []
        self.command_batch = 5
        self.memory_limit = 64
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

    def stop(self):
        self.stopped = True

    def abort(self):
        self.abort_queue = True

    def toggle_pause(self):
        self.paused = not self.paused

    def set_batchsize(self, bsize: int):
        with self.lock:
            self.command_batch = bsize

    def set_memory_limit(self, mlimit: int) -> None:
        with self.lock:
            self.memory_limit = mlimit

    def add_commands(self, commands: list[str], progress_cb: typing.Callable, curr_index: int = 0):
        with self.lock:
            self.commands = commands
            self.command_batch = min(self.command_batch, len(commands))
            self.progress_cb = progress_cb
            self.current_command_index = curr_index

        logging.info(f"Added {len(commands)} to async sender. batch: {self.command_batch}")

    def insert_commands(self, commands: list[str]):
        with self.lock:
            logging.info(f"Inserting {len(commands)} into async sender at index: {self.current_command_index}")
            self.commands[self.current_command_index : self.current_command_index] = commands

    def run(self):
        while not self.stopped:
            while self.current_command_index < len(self.commands):
                if self.abort_queue:
                    self.plotter.abort()
                    self.commands = []
                    self.current_command_index = 0
                    self.abort_queue = False
                    logging.info("Aborted AsyncSerialSender")
                    break

                end_index = min(self.current_command_index + self.command_batch, len(self.commands))
                with self.lock:
                    logging.info(f"Getting commands from index: {self.current_command_index}, end: {end_index}")
                    batched_commands = self.commands[self.current_command_index : end_index]
                    cmds = concat_commands(batched_commands)

                    if self.do_software_handshake:
                        requested_memory_amount = len(cmds)
                        free_io_memory = self.plotter.free_memory()

                        logging.info(
                            f"Free memory: {free_io_memory} requested: \
                            {requested_memory_amount} limit: {self.memory_limit}"
                        )

                        free_io_memory = min(free_io_memory, self.memory_limit)

                        if free_io_memory < requested_memory_amount:
                            sleep_time_seconds = 1
                            logging.info(f"Not enough free memory. Waiting {sleep_time_seconds}s")
                            time.sleep(sleep_time_seconds)
                            continue

                    logging.info(cmds)
                    self.plotter.write(cmds)

                    while self.paused:
                        time.sleep(0.1)

                    if self.send_single and not self.paused:
                        self.command_batch = 1
                        self.paused = True

                    self.current_command_index = end_index
                    time.sleep(0.01)

                    # call cb for progress
                    if self.progress_cb:
                        self.progress_cb(self.current_command_index)

            # after the currently set commands are done
            # empty the queue and reset the index
            self.commands = []
            self.current_command_index = 0

            # wait until new commands have been set
            time.sleep(1)


class SerialSender:
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
                    batched_commands = commands[i : i + command_batch]
                    cmds = concat_commands(batched_commands)
                    wait_for_free_io_memory(plotter, len(cmds))

                    plotter.write(cmds)
                    pbar.update(command_batch)
        except KeyboardInterrupt:
            logging.warning("Interrupted- aborting.")

            sleep(0.1)
            plotter.abort()
