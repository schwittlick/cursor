import configparser
import threading
from random import randint

import wasabi

import arcade
import arcade.gui

from cursor.collection import Collection
from cursor.device import MinmaxMapping, PlotterType
from tools.octet.data import all_paths

from tools.octet.discovery import discover
from tools.octet.gui import MainWindow, CheckerThread, TestButton
from tools.octet.launchpad_wrapper import NovationLaunchpad, reset_novation, set_novation_button, lp, novation_poll
from tools.octet.plotter import Plotter

logger = wasabi.Printer(pretty=True, no_print=False)

plotters = []

checker_thread = None

config = configparser.ConfigParser()

# Load the configuration file
config.read('config_client.ini')

# Get the values of the parameters
hostname = config.get('CONFIG', 'hostname')
target = config.get('CONFIG', 'target')

offline_mode = config.getboolean('CONFIG', 'offline_mode')

global_speed = 40


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):

        for plo in plotters:
            plo.close_serial()
            plo.client.close()

        if not lp:
            arcade.exit()
            return
        if lp.lp:
            lp.close()
        arcade.exit()
        # sys.exit()



# Define the key press callback function
def on_key_press(key, modifiers):
    global global_speed

    for plotter in plotters:
        if not plotter.thread:
            logger.warn(f"Ignored keypres bc plotter thread is not ready")
            continue
        #if not plotter.thread.running:
        if key == arcade.key.P:
            plotter.thread.add(Plotter.go_up_down)
        elif key == arcade.key.L:
            for i in range(4):
                plotter.thread.add(Plotter.draw_random_line)
        elif key == arcade.key.O:
            plotter.thread.add(Plotter.pen_down_up)
        elif key == arcade.key.I:
            plotter.thread.add(Plotter.random_pos)
        elif key == arcade.key.S:
            plotter.thread.add(Plotter.set_speed)
        elif key == arcade.key.Q:
            plotter.thread.add(Plotter.init)

        plotter.thread.resume()


def async_func(model, ip: str, tcp_port: int, serial_port: str, baud: int, timeout: float):
    p = Plotter(ip, tcp_port, serial_port, baud, timeout)
    p.connect()
    p.open_serial()

    plotter_map = {"7475A": PlotterType.HP_7475A_A3,
                   "7550A": PlotterType.HP_7550A,
                   "7595A": PlotterType.HP_7595A_A0,
                   "7596A": PlotterType.HP_7595A_A0}

    for k, v in plotter_map.items():
        if k == model:
            p.type = v
            return p

    return None


def connect_plotters(cfg, discovered) -> list:
    ip = target
    tcp_port = cfg.getint('CONFIG', 'port')
    baud = 9600
    timeout = config.getfloat('CONFIG', 'serial_timeout')

    results = []

    threads = []
    for plo in discovered:
        if not plo:
            continue
        serial_port = plo[0]
        model = plo[1]

        thread = threading.Thread(
            target=lambda: results.append(async_func(model, ip, tcp_port, serial_port, baud, timeout))
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(results)
    return results


if __name__ == '__main__':
    window = MainWindow()
    window.on_key_press = on_key_press
    window.add(QuitButton(text="Quit", width=200))

    if offline_mode:
        # add test plotter in offline mode
        test_plotter = Plotter("localhost", 12345, "/dev/ttyUSB0", 9600, 0.5)
        test_plotter.type = PlotterType.HP_7475A_A3
        test_plotter.connect()
        test_plotter.open_serial()
        plotters.append(test_plotter)
    else:
        discovered_plotters = discover()
        plotters = connect_plotters(config, discovered_plotters)

    checker_thread = CheckerThread(plotters)
    checker_thread.start()
    window.render_plotters(plotters)


    def on_change(v):
        logger.info(f"global_speed: {v}")
        global global_speed
        global_speed = v


    window.add_slider(on_change)
    window.finalize()
    arcade.run()

    # novation_poll(plotters)

    for plo in plotters:
        if plo.thread:
            plo.thread.stop()
            plo.thread.join()

    if checker_thread:
        checker_thread.stop()
        checker_thread.join()

    # p1.disconnect()
