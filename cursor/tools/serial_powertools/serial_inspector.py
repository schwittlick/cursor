import datetime
import logging
import threading
import time

import dearpygui.dearpygui as dpg
import serial
import serial.tools.list_ports

from cursor.hpgl import RESET_DEVICE, ABORT_GRAPHICS
from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.plotter.plotter import HPGLPlotter
from cursor.tools.discovery import discover
from cursor.tools.serial_powertools.bruteforce import run_brute_force
from cursor.tools.serial_powertools.seriallib import send_and_receive, SerialSender, AsyncSerialSender


# free static functions for the gui
def open_file_dialog(sender, app_data, user_data):
    # Opens the file dialog, allowing you to specify file types and a callback
    dpg.show_item("file_dialog")


def file_selected(sender, app_data, user_data):
    # app_data contains the selected file path and file name
    selected_file_dict = app_data['selections']
    if selected_file_dict:
        full_path = selected_file_dict[list(selected_file_dict.keys())[0]]
        dpg.set_value("file_path_text", full_path)


def print_output(text: str) -> None:
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%H:%M:%S")

    current_text = dpg.get_value("output_text")
    new_text = f"{timestamp_str}: {text}\n{current_text}".strip()
    dpg.set_value("output_text", new_text)


def refresh_serial_ports(sender, app_data, user_data):
    discovered_ports = discover(timeout=0.5)
    ports_with_model = [f"{port[0]} -> {port[1]}" for port in discovered_ports]
    dpg.configure_item("serial_port_dropdown", items=ports_with_model)


sending_file_paused = False
sending_file_running = False


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

        send_and_receive(self.serial_connection, command)

    def send_serial_command(self, sender, app_data, user_data):
        if not self.check():
            logging.warning(f"Serial connection not open.")
            return

        command = dpg.get_value("input_text")
        self.send_command(command)
        dpg.focus_item("input_text")

    def disconnect_serial(self, sender, app_data, user_data):
        if not self.check():
            logging.warning(f"Serial connection not open.")
            return

        self.serial_connection.close()
        logging.info(f"Disconnected from {self.serial_connection.port}")
        dpg.set_value("connection_status", "Disconnected")

    def connect_serial(self, sender, app_data, user_data):
        if self.check():
            logging.warning(f"Already connected to {self.serial_connection.port}")
            return

        try:
            serial_port_string = str(dpg.get_value("serial_port_dropdown")).split(" ")[0]
            serial_port_baud = dpg.get_value("baud_dropdown")
            self.serial_connection = serial.Serial(serial_port_string, serial_port_baud, timeout=1)
            dpg.set_value("connection_status", "Connected")
            print_output(f"Connected to {self.serial_connection.port}")
        except serial.SerialException as e:
            print_output(str(e))

    def stop_send_serial_file(self, sender, app_data, user_data):
        dpg.set_item_label("send_async_button", "Send Async")
        inspector.async_sender.stop()
        inspector.async_sender.join()
        logging.info(f"Stopped async sender. {inspector.async_sender.plotter}")

    def send_serial_file(self, sender, app_data, user_data):
        if not self.check():
            logging.warning(f"Serial connection not open.")
            return

        if inspector.async_sender:
            inspector.async_sender.pause()

            if inspector.async_sender.paused:
                dpg.set_item_label("send_async_button", "Resume")
            else:
                dpg.set_item_label("send_async_button", "Pause")

            return

        path_hpgl_file = dpg.get_value("file_path_text")
        hpgl_text = ''.join(open(path_hpgl_file, 'r', encoding='utf-8').readlines())

        commands = tokenizer(hpgl_text)

        plotter = HPGLPlotter(self.serial_connection)

        def progress_cb(command_idx: int):
            percentage = command_idx / len(commands)
            dpg.set_value("send_file_progress", percentage)
            dpg.configure_item("send_file_progress", overlay=f"{command_idx}/{len(commands)}")

        inspector.async_sender = AsyncSerialSender(plotter, commands, progress_cb)
        inspector.async_sender.do_software_handshake = False
        inspector.async_sender.command_batch = 1
        inspector.async_sender.start()

        dpg.set_item_label("send_async_button", "Pause")

    def pause_send_serial_file(self, sender, app_data, user_data):
        inspector.async_sender.pause()
        # logging.warn(f"Implement me. This should pause the not yet implemented thread that sends data to the plotter")

    def start_bruteforce_progress(self):
        for thread in self.bruteforce_threads:
            thread.stopped = True
            thread.join()
        serial_port_string = str(dpg.get_value("serial_port_dropdown")).split(" ")[0]
        baud_rates = [300, 1200, 9600, 19200, 115200]  # Baud rates to try
        parities = [serial.PARITY_NONE, serial.PARITY_ODD, serial.PARITY_EVEN]
        stop_bits = [serial.STOPBITS_ONE, serial.STOPBITS_TWO]
        xonxoff = [True]
        byte_sizes = [serial.SEVENBITS, serial.EIGHTBITS]

        timeout = float(dpg.get_value("timeout_dropdown"))

        message = "OI;"

        self.bruteforce_threads = run_brute_force([serial_port_string], baud_rates, parities, stop_bits, xonxoff,
                                                  byte_sizes, message,
                                                  timeout)


if __name__ == '__main__':
    inspector = SerialInspector()

    dpg.create_context()

    with dpg.file_dialog(directory_selector=False, show=False, callback=file_selected, tag="file_dialog", width=700,
                         height=400):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".hpgl", color=(255, 0, 0, 255), custom_text="[HPGL]")

    with dpg.window(label="Plotter Inspector", width=800, height=400):
        with dpg.group(horizontal=True):
            dpg.add_combo(label="Port", default_value="None", tag="serial_port_dropdown", width=200)
            dpg.add_combo(label="Baud", items=["1200", "9600"], default_value="9600", tag="baud_dropdown", width=100)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Refresh", callback=refresh_serial_ports)
            dpg.add_button(label="Connect", callback=inspector.connect_serial, tag="connect_button")
            dpg.add_button(label="Disconnect", callback=inspector.disconnect_serial, tag="disconnect_button")
            dpg.add_text("Status: Disconnected", tag="connection_status")

        with dpg.group(horizontal=True):
            dpg.add_input_text(label="Command", tag="input_text", on_enter=True, callback=inspector.send_serial_command)
            dpg.add_button(label="Send", callback=inspector.send_serial_command)

        with dpg.group(horizontal=True):
            dpg.add_button(label="IN;", callback=lambda: inspector.send_command("IN;"))
            dpg.add_button(label="OA;", callback=lambda: inspector.send_command("OA;"))
            dpg.add_button(label="OE;", callback=lambda: inspector.send_command("OE;"))
            dpg.add_button(label="OH;", callback=lambda: inspector.send_command("OH;"))
            dpg.add_button(label="OI;", callback=lambda: inspector.send_command("OI;"))
        with dpg.group(horizontal=True):
            dpg.add_button(label="PU;", callback=lambda: inspector.send_command("PU;"))
            dpg.add_button(label="PD;", callback=lambda: inspector.send_command("PD;"))

        with dpg.group(horizontal=True):
            dpg.add_button(label="VS1;", callback=lambda: inspector.send_command("VS1;"))
            dpg.add_button(label="VS10;", callback=lambda: inspector.send_command("VS10;"))
            dpg.add_button(label="VS20;", callback=lambda: inspector.send_command("VS20;"))
            dpg.add_button(label="VS40;", callback=lambda: inspector.send_command("VS40;"))
            dpg.add_button(label="VS80;", callback=lambda: inspector.send_command("VS80;"))
        with dpg.group(horizontal=True):
            dpg.add_button(label="PA0,0;", callback=lambda: inspector.send_command("PA0,0;"))
            dpg.add_button(label="PA10000,10000;", callback=lambda: inspector.send_command("PA10000,10000;"))

        with dpg.group(horizontal=True):
            dpg.add_button(label="ESC.R;", callback=lambda: inspector.send_command(f"{RESET_DEVICE};"))
            dpg.add_button(label="ESC.K;", callback=lambda: inspector.send_command(f"{ABORT_GRAPHICS};"))

        with dpg.group(horizontal=True):
            dpg.add_button(label="SP0;", callback=lambda: inspector.send_command("SP0;"))
            dpg.add_button(label="SP1;", callback=lambda: inspector.send_command("SP1;"))
            dpg.add_button(label="SP2;", callback=lambda: inspector.send_command("SP2;"))
            dpg.add_button(label="SP3;", callback=lambda: inspector.send_command("SP3;"))
            dpg.add_button(label="SP4;", callback=lambda: inspector.send_command("SP4;"))
            dpg.add_button(label="SP5;", callback=lambda: inspector.send_command("SP5;"))
            dpg.add_button(label="SP6;", callback=lambda: inspector.send_command("SP6;"))
            dpg.add_button(label="SP7;", callback=lambda: inspector.send_command("SP7;"))
            dpg.add_button(label="SP8;", callback=lambda: inspector.send_command("SP8;"))

    with dpg.window(label="Output", width=500, height=800, pos=(800, 0)):
        with dpg.child_window(height=650, autosize_x=True, horizontal_scrollbar=True):
            dpg.add_input_text(label="", multiline=True, readonly=True, tag="output_text", width=970, height=700)

    ports = [port.device for port in serial.tools.list_ports.comports()]
    dpg.configure_item("serial_port_dropdown", items=ports)


    # SEND FILE SECTION

    def run_task():
        global sending_file_paused
        global sending_file_running

        dpg.set_item_label("start_send_button", "Pause")

        for i in range(1, 101):
            while sending_file_paused:
                time.sleep(0.1)
            if not sending_file_running:
                return
            dpg.set_value("send_file_progress", 1 / 100 * (i))
            dpg.configure_item("send_file_progress", overlay=f"{i}%")
            time.sleep(0.005)

        sending_file_running = False
        sending_file_paused = False

        dpg.set_item_label("start_send_button", "Start")
        # progress bar finished


    def start_progress():
        global sending_file_paused
        global sending_file_running

        if not sending_file_running:
            logging.info(f"not runnng")
            sending_file_running = True
            sending_file_paused = False

            dpg.set_item_label("start_send_button", "Pause")

            thread = threading.Thread(target=run_task, args=(), daemon=True)
            thread.start()

            inspector.async_sender = AsyncSerialSender()
        else:
            logging.info(f"running..")
            if not sending_file_paused:
                sending_file_paused = True
                logging.info(f"pausing")
                dpg.set_item_label("start_send_button", "Resume")
            else:
                sending_file_paused = False
                dpg.set_item_label("start_send_button", "Pause")


    with dpg.window(label="Send file", width=800, height=200, pos=(0, 400)):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog"))
        with dpg.group(horizontal=True):
            dpg.add_input_text(label="", tag="file_path_text", readonly=True, width=700)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Send Async", tag="send_async_button", callback=inspector.send_serial_file)
            dpg.add_button(label="Stop sending", tag="stop_sending_button", callback=inspector.stop_send_serial_file)
        with dpg.group(horizontal=True):
            dpg.add_progress_bar(label="Progress", tag="send_file_progress")

    with dpg.window(label="Bruteforce", width=800, height=200, pos=(0, 600)):
        with dpg.group(horizontal=True):
            dpg.add_progress_bar(label="Bruteforce Progress", tag="bruteforce_progress")
            dpg.add_button(label="Bruteforce", tag="start_bruteforce_button",
                           callback=inspector.start_bruteforce_progress)
            dpg.add_combo(label="Timeout", items=["0.1", "0.3", "0.7", "1.0", "2.0"], default_value="1.0",
                          tag="timeout_dropdown", width=100)


    # SEND FILE SECTION

    def on_log(record):
        print_output(record.getMessage())
        return True


    logging.root.addFilter(on_log)

    dpg.create_viewport(title='Serial Inspector', width=1320, height=850)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
