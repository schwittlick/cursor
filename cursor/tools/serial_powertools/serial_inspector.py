import logging

import dearpygui.dearpygui as dpg
import serial.tools.list_ports

from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.plotter.plotter import HPGLPlotter
from cursor.tools.serial_powertools.bruteforce import run_brute_force
from cursor.tools.serial_powertools.seriallib import send_and_receive, AsyncSerialSender


# free static functions for the gui
def open_file_dialog(sender, app_data, user_data):
    # Opens the file dialog, allowing you to specify file types and a callback
    dpg.show_item("file_dialog")


class SerialInspector:
    """
    SerialInspector

    This gui app lets you easily debug a hpgl plotter by taking care of all the fiddly serial communication.
    """

    def __init__(self):
        self.serial_connection = serial.Serial()
        self.bruteforce_threads = []
        self.async_sender = None

    def check(self) -> bool:
        return self.serial_connection.is_open

    def send_command(self, command: str):
        if not self.check():
            logging.warning(f"Serial connection not open.")
            return

        received = send_and_receive(self.serial_connection, command)
        logging.info(f"Sent: {command}: {self.serial_connection.port} <- {received}")

    def send_serial_command(self, sender, app_data, user_data):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        command = dpg.get_value("input_text")
        self.send_command(command)
        dpg.focus_item("input_text")

    def disconnect_serial(self, sender, app_data, user_data):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        self.serial_connection.close()
        if self.async_sender:
            self.async_sender.stop()
        logging.info(f"Disconnected from {self.serial_connection.port}")
        dpg.set_value("connection_status", "Disconnected")

    def connect_serial(self, sender, app_data, user_data):
        if self.check():
            logging.warning(f"Already connected to {self.serial_connection.port}")
            return

        # if self.async_sender:
        #    self.serial_connection.close()

        try:
            serial_port_string = str(dpg.get_value("serial_port_dropdown")).split(" ")[0]
            serial_port_baud = dpg.get_value("baud_dropdown")
            self.serial_connection = serial.Serial(serial_port_string, serial_port_baud, timeout=1)
            dpg.set_value("connection_status", "Connected")
            logging.info(f"Connected to {self.serial_connection.port}")
        except serial.SerialException as e:
            logging.error(str(e))

            # self.async_sender.plotter.disconnect()

        # after successful serial connection
        # setup async sender for permanent interaction
        plotter = HPGLPlotter(self.serial_connection)

        self.async_sender = AsyncSerialSender(plotter)
        # self.async_sender.do_software_handshake = False  # for debugging purpos, don't check for buffer space
        self.async_sender.do_software_handshake = True
        self.async_sender.command_batch = 1
        self.async_sender.start()

    def stop_send_serial_file(self, sender, app_data, user_data):
        dpg.set_item_label("send_async_button", "Send Async")
        self.async_sender.abort()
        logging.info(f"Stopped async sender. {self.async_sender.plotter}")

    def send_serial_file(self, sender, app_data, user_data):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        logging.info(len(self.async_sender.commands))
        if len(self.async_sender.commands) > 0:
            if self.async_sender.paused:
                dpg.set_item_label("send_async_button", "Resume")
            return
            # self.async_sender.pause()

            # if self.async_sender.paused:
            #    dpg.set_item_label("send_async_button", "Resume")
            #    return
        else:
            dpg.set_item_label("send_async_button", "Pause")

        path_hpgl_file = dpg.get_value("file_path_text")
        logging.info(f"Sending {path_hpgl_file}")
        hpgl_text = ''.join(open(path_hpgl_file, 'r', encoding='utf-8').readlines())

        commands = tokenizer(hpgl_text)

        def progress_cb(command_idx: int):
            percentage = command_idx / len(commands)
            dpg.set_value("send_file_progress", percentage)
            dpg.configure_item("send_file_progress", overlay=f"{command_idx}/{len(commands)}")

        self.async_sender.add_commands(commands, progress_cb)

        dpg.set_item_label("send_async_button", "Pause")

    def pause_send_serial_file(self, sender, app_data, user_data):
        self.async_sender.pause()
        # logging.warn(f"Implement me. This should pause the not yet implemented thread that sends data to the plotter")

    def start_bruteforce_progress(self):
        # stopping previously running bruteforce threads
        for thread in self.bruteforce_threads:
            thread.stopped = True
            thread.join()

        serial_port_string = str(dpg.get_value("serial_port_dropdown")).split(" ")[0]
        baud_rates = [150, 300, 600, 1200, 2400, 4800, 9600, 19200, 115200]  # Baud rates to try
        parities = [serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_EVEN]
        stop_bits = [serial.STOPBITS_ONE, serial.STOPBITS_TWO]
        xonxoff = [True, False]
        byte_sizes = [serial.SEVENBITS, serial.EIGHTBITS]

        timeout = float(dpg.get_value("timeout_dropdown"))

        message = "OI;"

        self.bruteforce_threads = run_brute_force([serial_port_string], baud_rates, parities, stop_bits, xonxoff,
                                                  byte_sizes, message,
                                                  timeout)

    def stop_bruteforce_progress(self):
        for thread in self.bruteforce_threads:
            thread.stopped = True
            thread.join()

        dpg.set_value("bruteforce_progress", 0)
        logging.info("Stopped bruteforce threads")

    def get_plotter_model(self):
        if not self.check():
            logging.warning("Serial connection not open.")
            return

        model = self.async_sender.plotter.identify()
        dpg.set_value("plotter_model", model)
