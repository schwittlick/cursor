import configparser
import threading
import wasabi
import arcade
import arcade.gui

from cursor.device import PlotterType

from tools.octet.discovery import discover
from tools.octet.gui import MainWindow
from tools.octet.launchpad import NovationLaunchpad
from tools.octet.midique import Midique
from tools.octet.plotter import Plotter, CheckerThread

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
USE_MIDIQUE = config.getboolean('CONFIG', 'midique')
USE_LAUNCHPAD = config.getboolean('CONFIG', 'launchpad')


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        for plo in plotters:
            if plo.serial_port:
                plo.close_serial()
                plo.client.close()

        arcade.exit()


def async_func(model, ip: str, tcp_port: int, serial_port: str, baud: int, timeout: float):
    p = Plotter(ip, tcp_port, serial_port, baud, timeout)
    p.connect()
    p.open_serial()

    plotter_map = {"7475A": PlotterType.HP_7475A_A3,
                   "7550A": PlotterType.HP_7550A,
                   "7595A": PlotterType.HP_7596B,
                   "7596A": PlotterType.HP_7596B}

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
    window.add(QuitButton(text="Quit", width=200))

    if offline_mode:
        # add test plotter in offline mode
        for i in range(8):
            test_plotter = Plotter("localhost", 12345, None, 9600, 0.5)
            test_plotter.type = PlotterType.HP_7475A_A3
            test_plotter.client.set_timeout(0.1)
            test_plotter.connect()
            # test_plotter.open_serial()
            plotters.append(test_plotter)
    else:
        discovered_plotters = discover()
        plotters = connect_plotters(config, discovered_plotters)

    window.plotters = plotters
    window.render_plotters()

    checker_thread = CheckerThread(plotters)
    checker_thread.start()


    def on_change(v):
        logger.info(f"setting speed for all: {v}")
        for plo in plotters:
            plo.thread.speed = v


    window.add_slider(on_change)
    window.finalize()

    if USE_MIDIQUE:
        midique = Midique()
        for i in range(len(plotters)):
            midique.connect((32 + 3) + i * 4, plotters[i].set_delay)
        midique.listen()

    if USE_LAUNCHPAD:
        lp = NovationLaunchpad()
        for i in range(len(plotters)):
            p = plotters[i]
            lp.connect(0 + i, lambda _p=p: _p.thread.add(_p.go_up_down))
            lp.connect(16 + i, lambda _p=p: _p.thread.add(_p.c73))
            lp.connect(32 + i, lambda _p=p: _p.thread.add(_p.draw_random_line))
            lp.connect(48 + i, lambda _p=p: _p.thread.add(_p.pen_down_up))

            lp.connect(104 + i, lambda _p=p: _p.thread.add(_p.reset))
        lp.listen()

    arcade.run()

    if USE_MIDIQUE:
        midique.stop()

    if USE_LAUNCHPAD:
        lp.stop()

    for plo in plotters:
        if plo.thread:
            plo.thread.stop()
            plo.thread.join()

    if checker_thread:
        checker_thread.stop()
        checker_thread.join()

    # p1.disconnect()
