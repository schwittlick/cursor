import configparser
import logging
import pathlib
import threading
import wasabi

import arcade
import arcade.gui

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import Paper, PaperSize, XYFactors, MinmaxMapping, PlotterType
from cursor.loader import Loader
from cursor.renderer import HPGLRenderer

from tools.octet.discovery import discover
from tools.octet.gui import MainWindow, GuiThread, CheckerThread
from tools.octet.launchpad_wrapper import NovationLaunchpad, reset_novation, set_novation_button, lp, novation_poll
from tools.octet.plotter import Plotter

logger = wasabi.Printer(pretty=True, no_print=False)

recordings = DataDirHandler().recordings()
_loader = Loader(directory=recordings, limit_files=1)
all_paths = _loader.all_paths()

gui_threads = {}

plotters = []

checker_thread = None

config = configparser.ConfigParser()

# Load the configuration file
config.read('config_client.ini')

# Get the values of the parameters
hostname = config.get('CONFIG', 'hostname')
target = config.get('CONFIG', 'target')
port = config.getint('CONFIG', 'port')
offline_mode = config.getboolean('CONFIG', 'offline_mode')


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        if not lp:
            arcade.exit()
            return
        if lp.lp:
            lp.close()
        arcade.exit()
        # sys.exit()


def run_blocking_process(_plotter):
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

    return feedback


class TestButton(arcade.gui.UIFlatButton):
    def __init__(self, plotter, **kwargs):
        super().__init__(**kwargs)
        self.plotter = plotter

    def on_click(self, event: arcade.gui.UIOnClickEvent):
        global gui_threads
        if not self.plotter.port in gui_threads.keys():
            # if not process_running[plotter.serial_port]:
            thread = GuiThread(self.plotter.port)
            thread.plotter = self.plotter
            thread.func = run_blocking_process
            thread.start()

            gui_threads[self.plotter.port] = thread

        global process_running
        if not process_running[self.plotter.serial_port]:
            process_thread = threading.Thread(target=run_blocking_process, args=(self.plotter,))
            process_thread.start()
            # process_thread.join()  # Wait for the thread to finish
            logger.good(f"finished starting thread for {self.plotter.serial_port}")

        else:
            logger.warn(f"discarding data for {self.plotter.serial_port}")


def go_up_down(_plotter):
    d = MinmaxMapping.maps[_plotter.type]
    result, feedback = _plotter.send_data(f"PU;PA{d.x},{0};PA{d.w},{0}")

    print(f"done with updown {result} + {feedback}")

    return feedback


# Define the key press callback function
def on_key_press(key, modifiers):
    global process_running
    global gui_threads

    for plotter in plotters:
        if not plotter.port in gui_threads.keys():
            thread = GuiThread(plotter.port)
            thread.plotter = plotter

            if key == arcade.key.P:
                thread.func = go_up_down
            elif key == arcade.key.L:
                thread.func = run_blocking_process

            # only start if no other thread for this port is running
            thread.start()

            gui_threads[plotter.port] = thread

            logger.good(f"finished starting thread for {plotter.serial_port}")

        else:
            logger.warn(f"discarding data for {plotter.serial_port}")


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
    plotter_map = {"7475A": PlotterType.HP_7475A_A3,
                   "7550A": PlotterType.HP_7550A,
                   "7595A": PlotterType.HP_7595A,
                   "7576B": PlotterType.HP_7596B}

    window = MainWindow()
    window.on_key_press = on_key_press
    window.add(QuitButton(text="Quit", width=200))

    discovered_plotters = discover()

    checker_thread = CheckerThread(gui_threads)
    checker_thread.start()

    if offline_mode:
        # add test plotter in offline mode
        test_plotter = Plotter("localhost", 12345, "/dev/ttyUSB0", 9600, 0.5)
        test_plotter.type = PlotterType.HP_7475A_A3
        test_plotter.connect()
        test_plotter.open_serial()
        plotters.append(test_plotter)

        tb1 = TestButton(text=f"Test Plotter", width=200, plotter=test_plotter)
        window.add(tb1)

    for plo in discovered_plotters:
        ip = target
        tcp_port = port
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

    # novation_poll(plotters)

    for thread in gui_threads:
        thread.join()

    # Stop the checker thread
    checker_thread.stop()
    checker_thread.join()

    # p1.disconnect()
