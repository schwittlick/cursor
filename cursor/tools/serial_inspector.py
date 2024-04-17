import datetime

import dearpygui.dearpygui as dpg
import serial
import serial.tools.list_ports

from cursor.hpgl import read_until_char
from cursor.hpgl.hpgl_tokenize import tokenizer
from cursor.hpgl.plotter.plotter import HPGLPlotter
from cursor.tools.sendhpgl import SerialSender


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
    ports = [port.device for port in serial.tools.list_ports.comports()]
    dpg.configure_item("serial_port_dropdown", items=ports)


class SerialInspector:
    """
    SerialInspector

    This gui app lets you easily debug a hpgl plotter by taking care of all the fiddly serial communication.
    """

    def __init__(self):
        self.serial_connection = serial.Serial()

    def check(self) -> bool:
        return self.serial_connection.is_open

    def send_command(self, command):
        if not self.check():
            print_output(f"Serial connection not open.")
            return

        try:
            self.serial_connection.write(command.encode())
            print_output(f"{self.serial_connection.port} <- {command}")
            received_data = read_until_char(self.serial_connection)
            print_output(f"{self.serial_connection.port} -> {received_data}")
        except serial.SerialException as e:
            print_output(str(e))

    def send_serial_command(self, sender, app_data, user_data):
        if not self.check():
            print_output(f"Serial connection not open.")
            return

        command = dpg.get_value("input_text")
        self.send_command(command)
        dpg.focus_item("input_text")

    def disconnect_serial(self, sender, app_data, user_data):
        if not self.check():
            print_output(f"Serial connection not open.")
            return

        self.serial_connection.close()
        print_output(f"Disconnected from {self.serial_connection.port}")
        dpg.set_value("connection_status", "Disconnected")

    def connect_serial(self, sender, app_data, user_data):
        if self.check():
            print_output(f"Already connected to {self.serial_connection.port}")
            return

        try:
            serial_port_string = dpg.get_value("serial_port_dropdown")
            serial_port_baud = dpg.get_value("baud_dropdown")
            self.serial_connection = serial.Serial(serial_port_string, serial_port_baud, timeout=1)
            dpg.set_value("connection_status", "Connected")
            print_output(f"Connected to {self.serial_connection.port}")
        except serial.SerialException as e:
            print_output(str(e))

    def send_serial_file(self, sender, app_data, user_data):
        if not self.check():
            print_output(f"Serial connection not open.")
            return

        path_hpgl_file = dpg.get_value("file_path_text")
        hpgl_text = ''.join(open(path_hpgl_file, 'r', encoding='utf-8').readlines())

        commands = tokenizer(hpgl_text)

        plotter = HPGLPlotter(self.serial_connection)

        SerialSender().send(plotter, commands)


if __name__ == '__main__':
    inspector = SerialInspector()

    dpg.create_context()

    with dpg.file_dialog(directory_selector=False, show=False, callback=file_selected, tag="file_dialog", width=700,
                         height=400):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".hpgl", color=(255, 0, 0, 255), custom_text="[HPGL]")

    with dpg.window(label="Plotter Inspector", width=1000, height=800):
        with dpg.group(horizontal=True):
            dpg.add_combo(label="Port", default_value="None", tag="serial_port_dropdown", width=200)
            dpg.add_combo(label="Baud", items=["1200", "9600"], default_value="9600", tag="baud_dropdown", width=100)
            dpg.add_button(label="Refresh", callback=refresh_serial_ports)
            dpg.add_button(label="Connect", callback=inspector.connect_serial, tag="connect_button")
            dpg.add_button(label="Disconnect", callback=inspector.disconnect_serial, tag="disconnect_button")
            dpg.add_text("Status: Disconnected", tag="connection_status")

        with dpg.group(horizontal=True):
            dpg.add_input_text(label="Command", tag="input_text", on_enter=True, callback=inspector.send_serial_command)
            dpg.add_button(label="Send", callback=inspector.send_serial_command)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_input_text(label="Selected File Path", tag="file_path_text", readonly=True, width=700)
            dpg.add_button(label="Send", callback=inspector.send_serial_file)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Send OA;", callback=lambda: inspector.send_command("OA;"))
            dpg.add_button(label="Send OE;", callback=lambda: inspector.send_command("OE;"))
            dpg.add_button(label="Send OH;", callback=lambda: inspector.send_command("OH;"))
            dpg.add_button(label="Send OI;", callback=lambda: inspector.send_command("OI;"))

        with dpg.child_window(height=650, autosize_x=True, horizontal_scrollbar=True):
            dpg.add_input_text(label="", multiline=True, readonly=True, tag="output_text", width=970, height=700)

    refresh_serial_ports(None, None, None)

    dpg.create_viewport(title='Serial Inspector', width=1020, height=850)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
