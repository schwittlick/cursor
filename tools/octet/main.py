import pathlib
import threading

import arcade
import arcade.gui

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import Paper, PaperSize, XYFactors, MinmaxMapping, PlotterType
from cursor.loader import Loader
from cursor.renderer import HPGLRenderer
from cursor.timer import Timer
from tools.octet.discovery import discover
from tools.octet.gui import MainWindow
from tools.octet.launchpad_wrapper import NovationLaunchpad

from tools.octet.plotter import Plotter
import wasabi
import time
import sys

logger = wasabi.Printer(pretty=True, no_print=False)

recordings = DataDirHandler().recordings()
_loader = Loader(directory=recordings, limit_files=1)
all_paths = _loader.all_paths()

process_running = {}

plotters = []

class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        if lp.lp:
            lp.close()
        arcade.exit()
        sys.exit()


def run_blocking_process(_plotter):
    global process_running
    process_running[_plotter.serial_port] = True

    feedback = ""
    for i in range(2):
        # Replace this with your own blocking process
        c = Collection()
        line = all_paths.random()
        line.velocity = 110
        c.add(line)
        d = rendering(c, _plotter.type)
        # print(f"data: {d}")
        result, feedback = _plotter.send_data(d)
        print(f"done with button {result} + {feedback}")

    process_running[_plotter.serial_port] = False
    return feedback


class TestButton(arcade.gui.UIFlatButton):
    def __init__(self, plotter, **kwargs):
        super().__init__(**kwargs)
        self.plotter = plotter

    def on_click(self, event: arcade.gui.UIOnClickEvent):

        global process_running
        if not process_running[self.plotter.serial_port]:
            process_thread = threading.Thread(target=run_blocking_process, args=(self.plotter,))
            process_thread.start()
            # process_thread.join()  # Wait for the thread to finish
            logger.good(f"finished starting thread for {self.plotter.serial_port}")

        else:
            logger.warn(f"discarding data for {self.plotter.serial_port}")


USE_NOVATION = True


def go_up_down(_plotter):
    global process_running
    process_running[_plotter.serial_port] = True
    d = MinmaxMapping.maps[_plotter.type]
    result, feedback = _plotter.send_data(f"PU;PA{d.x},{d.y};PA{d.w},{d.h}")

    print(f"done with updown {result} + {feedback}")

    process_running[_plotter.serial_port] = False
    return feedback

# Define the key press callback function
def on_key_press(key, modifiers):
    global process_running

    if key == arcade.key.P:
        for plotter in plotters:
            if not process_running[plotter.serial_port]:
                process_thread = threading.Thread(target=go_up_down, args=(plotter,))
                process_thread.start()
                # process_thread.join()  # Wait for the thread to finish
                logger.good(f"finished starting thread for {plotter.serial_port}")

            else:
                logger.warn(f"discarding data for {plotter.serial_port}")
    elif key == arcade.key.L:
        for plotter in plotters:
            if not process_running[plotter.serial_port]:
                process_thread = threading.Thread(target=run_blocking_process, args=(plotter,))
                process_thread.start()
                # process_thread.join()  # Wait for the thread to finish
                logger.good(f"finished starting thread for {plotter.serial_port}")

            else:
                logger.warn(f"discarding data for {plotter.serial_port}")


def log(tup):
    success, msg = tup
    if success:
        logger.good(msg)
    else:
        logger.fail(msg)


def set_novation_button(data, x: int, y: int, state: bool):
    if not lp:
        return
    value = 1 if state else 0
    lp.lp.LedCtrlXY(data[x], data[y], value, value)


def reset_novation():
    logger.warn("RESET Novation")
    if not lp.lp:
        return
    for i in range(8):
        for j in range(8):
            lp.lp.LedCtrlXY(i, j, 0, 0)


def rendering(collection: Collection, type: PlotterType) -> str:
    collection.fit(
        Paper.sizes[PaperSize.LANDSCAPE_A3],
        xy_factor=XYFactors.fac[type],
        padding_mm=20,
        output_bounds=MinmaxMapping.maps[type],
        keep_aspect=True
    )

    r = HPGLRenderer(pathlib.Path(""))
    r.render(collection)
    return r.generate_string()


if __name__ == '__main__':
    plotter_map = {"7475A": PlotterType.HP_7475A_A3, "7550A": PlotterType.HP_7550A}

    if USE_NOVATION:
        lp = NovationLaunchpad()
        reset_novation()

    window = MainWindow()
    window.on_key_press = on_key_press
    window.add(QuitButton(text="Quit", width=200))

    discovered_plotters = discover()

    for plo in discovered_plotters:
        ip = "192.168.2.124"
        tcp_port = 12345
        baud = 9600
        timeout = 0.5
        port = plo[0]
        process_running[port] = False

        p = Plotter(ip, tcp_port, port, baud, timeout)
        p.connect()
        p.open_serial()
        success, model = p.get_model()
        if success:
            print(f"success opening {port} -> {model}")
            plotters.append(p)

            for k, v in plotter_map.items():
                if k == model:
                    p.type = v
                    tb1 = TestButton(text=f"Plotter {model}", width=200, plotter=p)
                    window.add(tb1)
        else:
            p.close_serial()
            p.disconnect()

    window.finalize()
    arcade.run()

    timer = Timer()
    while True:
        time.sleep(0.001)
        CONNECT_Y = 1

        if not lp.lp:
            continue

        button = lp.poll()

        if button != []:
            logger.info(button)

            if button[0] == 0 and button[1] == 0:
                reset_novation()

                continue

            p = plotters[button[0]]
            if button[2]:
                set_novation_button(button, 0, 1, True)
            else:
                # if serial is open, close it
                if p.is_connected:
                    p.is_open_serial()
                    is_serial_open, msg = p.recv()
                    if is_serial_open:
                        p.close_serial()
                        success, data = p.recv()
                        logger.info(f"closing serial {success} -> {data}")
                        if success:
                            set_novation_button(button, 0, 1, False)
                        else:
                            set_novation_button(button, 0, 1, True)
                    else:
                        # otherwise open it
                        p.open_serial()
                        success, data = p.recv()
                        logger.info(f"opening serial {success} -> {data}")
                        if success:
                            p.get_model()
                            success, data = p.recv()
                            logger.info(success, data)
                            if success:
                                set_novation_button(button, 0, 1, True)
                            else:
                                set_novation_button(button, 0, 1, False)
                        else:
                            set_novation_button(button, 0, 1, False)
                else:
                    logger.warn(f"Not connected to {p}")
    timer.print_elapsed("end")

    # p1.disconnect()
