import datetime
import logging
import random
import typing

import dearpygui.dearpygui as dpg
import serial

from cursor.collection import Collection
from cursor.device import PlotterHpglNames, MinmaxMapping
from cursor.hpgl import RESET_DEVICE, ABORT_GRAPHICS
from cursor.path import Path
from cursor.renderer.hpgl import HPGLRenderer
from cursor.tools.discovery import discover
from cursor.tools.serial_powertools.serial_inspector import SerialInspector
from data.compositions.composition98.ink_drink import generate_circled_line


def print_output(text: str) -> None:
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%H:%M:%S")

    current_text = dpg.get_value("output_text")
    new_text = f"{timestamp_str}: {text}\n{current_text}".strip()
    dpg.set_value("output_text", new_text)


def file_selected(sender, app_data, user_data):
    # app_data contains the selected file path and file name
    selected_file_dict = app_data['selections']
    if selected_file_dict:
        full_path = selected_file_dict[list(selected_file_dict.keys())[0]]
        dpg.set_value("file_path_text", full_path)


def refresh_serial_ports(sender, app_data, user_data):
    logging.info("Starting refresh..")
    discovered_ports = discover(timeout=0.5)
    ports_with_model = [f"{port[0]} -> {port[1]}" for port in discovered_ports]
    dpg.configure_item("serial_port_dropdown", items=ports_with_model)


def create_file_dialogue(cb: typing.Callable):
    with dpg.file_dialog(directory_selector=False, show=False, callback=cb, tag="file_dialog", width=700,
                         height=400):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".hpgl", color=(255, 0, 0, 255), custom_text="[HPGL]")


def generate_random_swirl() -> str:
    units_per_mm = 40
    diameter_mm = 10
    lines = 30
    speed = 1

    collection = Collection()

    offset_x = random.uniform(0, 10000)
    offset_y = random.uniform(0, 10000)

    p = Path()
    p.velocity = speed
    p.pen_select = 1

    for l in range(lines):
        diameter_units = diameter_mm * units_per_mm
        x = random.uniform(-diameter_units, diameter_units)
        y = random.uniform(-diameter_units, diameter_units)

        x += offset_x
        y += offset_y

        p.add(x, y)

    collection.add(p)
    hpgl_code = HPGLRenderer.generate_string(collection)

    return hpgl_code


def generate_circled_line_gui() -> str:
    path = generate_circled_line()
    collection = Collection()
    collection.add(path)
    collection.add(path.copy())
    collection.add(path.copy())
    collection.add(path.copy())
    collection.add(path.copy())
    collection.add(path.copy())

    collection2 = collection.copy()
    collection2.translate(50, 0)
    collection3 = collection.copy()
    collection3.translate(100, 0)

    collection4 = collection.copy()
    collection4.translate(150, 0)
    collection5 = collection.copy()
    collection5.translate(200, 0)
    collection6 = collection.copy()
    collection6.translate(250, 0)
    collection7 = collection.copy()
    collection7.translate(300, 0)
    collection8 = collection.copy()
    collection8.translate(350, 0)
    collection9 = collection.copy()
    collection9.translate(400, 0)
    collection10 = collection.copy()
    collection10.translate(450, 0)

    hpgl_code = HPGLRenderer.generate_string(collection)

    hpgl_code += HPGLRenderer.generate_string(collection2)
    hpgl_code += HPGLRenderer.generate_string(collection3)
    hpgl_code += HPGLRenderer.generate_string(collection4)
    hpgl_code += HPGLRenderer.generate_string(collection5)
    hpgl_code += HPGLRenderer.generate_string(collection6)
    hpgl_code += HPGLRenderer.generate_string(collection7)
    hpgl_code += HPGLRenderer.generate_string(collection8)
    hpgl_code += HPGLRenderer.generate_string(collection9)
    hpgl_code += HPGLRenderer.generate_string(collection10)
    return hpgl_code


def generate_random_dot_walk() -> str:
    plotter_model = "DXY-1200"

    potential_plotters = PlotterHpglNames.names[plotter_model]
    guessed_plotter = potential_plotters[0]  # a3 size is the expected default here

    bb = MinmaxMapping.maps[guessed_plotter]

    x = random.randint(bb.x, bb.x2)
    y = random.randint(bb.y, bb.y2)

    data = "SP1;VS1;PU;"
    data += f"PA{x},{y};"

    variance = 60

    dots = 30000
    for i in range(dots):
        x_variance = random.randint(-variance, variance)
        y_variance = random.randint(-variance, variance)
        if not 0 < x + x_variance < bb.w:
            x = random.randint(bb.x, bb.x2)
        else:
            x += x_variance
        if not 0 < y + y_variance < bb.h:
            y = random.randint(bb.y, bb.y2)
        else:
            y += y_variance
        # here try to keep things in the plotter bb!
        data += f"PA{x},{y};"
        data += "PD;"
        data += f"PA{x + 10},{y + 10};"
        data += "PU;"

    data += "SP0;PA0,0;"

    return data


def generate_filled_square_lines(inspector: SerialInspector) -> str:
    plotter_model = "DXY-1200"

    potential_plotters = PlotterHpglNames.names[plotter_model]
    guessed_plotter = potential_plotters[0]  # a3 size is the expected default here

    bb = MinmaxMapping.maps[guessed_plotter]

    w = random.randint(100, 2000)
    h = random.randint(100, 2000)

    # subtract w/h so we don't go out of bounds
    x = random.randint(bb.x, bb.x2 - w)
    y = random.randint(bb.y, bb.y2 - h)

    data = "VS1;SP1;VS1;PU;"
    data += f"PA{x},{y};"

    stepsize = 25  # 25 also ok?
    repetitions = 3

    for rep in range(repetitions):
        for x_step in range(x, x + w, stepsize):
            data += f"PA{x_step},{y};"
            data += "PD;"
            data += f"PA{x_step},{y + h};"
            data += "PU;"

    return data


def generate_filled_square_dotted(inspector: SerialInspector) -> str:
    plotter_model = "DXY-1200"

    potential_plotters = PlotterHpglNames.names[plotter_model]
    guessed_plotter = potential_plotters[0]  # a3 size is the expected default here

    bb = MinmaxMapping.maps[guessed_plotter]

    w = random.randint(100, 2000)
    h = random.randint(100, 2000)

    # subtract w/h so we don't go out of bounds
    x = random.randint(bb.x, bb.x2 - w)
    y = random.randint(bb.y, bb.y2 - h)

    data = "VS1;SP1;VS1;PU;"
    data += f"PA{x},{y};"

    stepsize = 25  # 25 also ok?
    repetition = 3

    for x_step in range(x, x + w, stepsize):
        for y_step in range(y, y + h, stepsize):
            for rep in range(repetition):
                data += f"PA{x_step},{y_step};"
                data += "PD;"
                data += f"PA{x_step + 10},{y_step + 10};"
                data += "PU;"

    return data


def generate_random_pa() -> str:
    x = random.randint(0, 10000)
    y = random.randint(0, 10000)
    return f"PA{x},{y};"


def create_plotter_inspector_gui(inspector: SerialInspector):
    with dpg.window(label="Inspector"):
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
            dpg.add_button(label="PArandom(),random();", callback=lambda: inspector.send_command(generate_random_pa()))

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

        with dpg.group(horizontal=True):
            dpg.add_button(label="Random Swirl (ink drink)",
                           callback=lambda: inspector.send_command(generate_random_swirl()))
            dpg.add_button(label="Random Circled Line (ink drink)",
                           callback=lambda: inspector.send_command(generate_circled_line_gui()))
            dpg.add_button(label="Random dot walk",
                           callback=lambda: inspector.send_command(generate_random_dot_walk()))
            dpg.add_button(label="Fill square (dotted)",
                           callback=lambda: inspector.send_command(generate_filled_square_dotted(inspector)))
            dpg.add_button(label="Fill square (lines)",
                           callback=lambda: inspector.send_command(generate_filled_square_lines(inspector)))

    ports = [port.device for port in serial.tools.list_ports.comports()]
    dpg.configure_item("serial_port_dropdown", items=ports)


def add_output_window():
    with dpg.window(label="Output", width=700, height=800, pos=(800, 0)):
        with dpg.child_window(autosize_x=True, horizontal_scrollbar=True):
            dpg.add_input_text(label="", multiline=True, readonly=True, tag="output_text", width=650, height=800)


def create_send_file_gui(inspector: SerialInspector):
    with dpg.window(label="Send file", pos=(0, 400)):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Select File", callback=lambda: dpg.show_item("file_dialog"))
        with dpg.group(horizontal=True):
            dpg.add_input_text(label="", tag="file_path_text", readonly=True, width=700)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Send Async", tag="send_async_button", callback=inspector.send_serial_file)
            dpg.add_button(label="Stop sending", tag="stop_sending_button", callback=inspector.stop_send_serial_file)
        with dpg.group(horizontal=True):
            dpg.add_progress_bar(label="Progress", tag="send_file_progress")


def create_bruteforce_gui(inspector: SerialInspector):
    with dpg.window(label="Bruteforce", pos=(0, 600)):
        with dpg.group(horizontal=True):
            dpg.add_progress_bar(label="Bruteforce Progress", tag="bruteforce_progress")
        with dpg.group(horizontal=True):
            dpg.add_button(label="Bruteforce", tag="start_bruteforce_button",
                           callback=inspector.start_bruteforce_progress)
            dpg.add_button(label="Stop Bruteforce", tag="stop_bruteforce_button",
                           callback=inspector.stop_bruteforce_progress)
            dpg.add_combo(label="Timeout", items=["0.1", "0.3", "0.7", "1.0", "2.0"], default_value="1.0",
                          tag="timeout_dropdown", width=100)


def add_plotter_info_window(inspector: SerialInspector):
    with dpg.window(label="Plotter Info", pos=(0, 300)):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Get model", tag="get_plotter_model", callback=inspector.get_plotter_model)
            dpg.add_text(label="Plotter Model", tag="plotter_model")


if __name__ == '__main__':
    print(generate_random_swirl())
