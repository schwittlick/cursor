import configparser
import threading
import wasabi
import arcade.gui

from cursor.device import PlotterType, MaxSpeed

from tools.octet.discovery import discover
from tools.octet.gui import MainWindow
from tools.octet.launchpad import NovationLaunchpad
from tools.octet.midique import Midique
from tools.octet.plotter import Plotter
from tools.octet.plotterthread import CheckerThread

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


def async_func(model, ip: str, tcp_port: int, serial_port: str, baud: int, timeout: float, pen_count: int):
    p = Plotter(ip, tcp_port, serial_port, baud, timeout, pen_count)
    p.connect()
    p.open_serial()

    plotter_map = {"7475A": PlotterType.HP_7475A_A3,
                   "7550A": PlotterType.HP_7550A,
                   "7595A": PlotterType.HP_7595A,
                   "7596A": PlotterType.HP_7596A}

    for k, v in plotter_map.items():
        if k == model:
            p.type = v
            p.thread.speed = MaxSpeed.fac[v]
            return p

    return None


def connect_plotters(cfg, discovered) -> list:
    ip = target
    tcp_port = cfg.getint('CONFIG', 'port')
    baud = 9600
    timeout = config.getfloat('CONFIG', 'serial_timeout')
    PEN_COUNT = config.getint('CONFIG', 'pens')

    results = []

    threads = []
    for plo in discovered:
        if not plo:
            continue
        serial_port = plo[0]
        model = plo[1]

        thread = threading.Thread(
            target=lambda: results.append(async_func(model, ip, tcp_port, serial_port, baud, timeout, PEN_COUNT))
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results = sorted(
        results,
        key=lambda x: x.type.value
    )

    return results


if __name__ == '__main__':
    window = MainWindow()

    if offline_mode:
        # add test plotter in offline mode
        for i in range(8):
            test_plotter = Plotter("localhost", 12345, None, 9600, 0.5, 2)
            test_plotter.type = PlotterType.HP_7475A_A3
            test_plotter.client.set_timeout(0.1)
            test_plotter.connect()
            # test_plotter.open_serial()
            plotters.append(test_plotter)
    else:
        discovered_plotters = discover()
        plotters = connect_plotters(config, discovered_plotters)

    window.plotters = plotters
    window.add_labels()
    window.render_plotters()

    checker_thread = CheckerThread(plotters)
    checker_thread.start()


    def on_change(v):
        logger.info(f"setting speed for all: {v}")
        for plo in plotters:
            plo.thread.speed = v


    # window.add_slider(on_change)
    window.finalize()

    if USE_MIDIQUE:
        midique = Midique()
        for i in range(len(plotters)):
            plo = plotters[i]
            midique.connect((29 + 3) + i * 4, lambda sp, _p=plo: _p.set_value1(sp))
            midique.connect((30 + 3) + i * 4, lambda sp, _p=plo: _p.set_value2(sp))
            midique.connect((31 + 3) + i * 4, lambda d, _p=plo: _p.set_line_distance(d))
            midique.connect((32 + 3) + i * 4, lambda sp, _p=plo: _p.set_speed(sp))


        def set_master_v1(v, _plotters):
            for p in _plotters:
                p.set_value1(v)


        def set_master_v2(v, _plotters):
            for p in _plotters:
                p.set_value2(v)


        def set_master_speed(v, _plotters):
            for p in _plotters:
                p.set_speed(v)


        def set_master_line_distance(v, _plotters):
            for p in _plotters:
                p.set_line_distance(v)


        midique.connect(64, lambda sp, pl=plotters: set_master_v1(sp, pl))
        midique.connect(65, lambda sp, pl=plotters: set_master_v2(sp, pl))
        midique.connect(66, lambda sp, pl=plotters: set_master_line_distance(sp, pl))
        midique.connect(67, lambda sp, pl=plotters: set_master_speed(sp, pl))
        midique.listen()

    if USE_LAUNCHPAD:
        lp = NovationLaunchpad()


        def add_pen_up_down(_plotters):
            for p in _plotters:
                if p.type == PlotterType.HP_7475A_A3:
                    p.thread.add(p.pen_down_up)


        def add_simulated(_plotters):
            print("SIMULATED")
            for p in _plotters:
                p.thread.add(p.chatgpt_simulated_mouse_movement)


        # button on very right
        lp.connect(8, lambda _p=plotters: [pp.thread.add(pp.mouse) for pp in _p])
        lp.connect(16 + 8, lambda _p=plotters: [pp.thread.add(pp.c73) for pp in _p])
        lp.connect(32 + 8, lambda _p=plotters: [pp.thread.add(pp.draw_random_line) for pp in _p])
        lp.connect(48 + 8,
                   lambda _plotters=plotters: add_pen_up_down(_plotters))
        lp.connect(64 + 8,
                   lambda _p=plotters: [pp.thread.add(pp.c83) for pp in _p])
        lp.connect(80 + 8,
                   lambda _p=plotters: [pp.thread.add(pp.small_line_field) for pp in _p])
        lp.connect(96 + 8,
                   lambda _p=plotters: add_simulated(_p))
        lp.connect(112 + 8, lambda _p=plotters: [pp.thread.add(pp.next_pen) for pp in _p])

        for i in range(len(plotters)):
            p = plotters[i]
            lp.connect(0 + i, lambda _p=p: _p.thread.add(_p.mouse))
            lp.connect(16 + i, lambda _p=p: _p.thread.add(_p.c73))
            lp.connect(32 + i, lambda _p=p: _p.thread.add(_p.draw_random_line))
            lp.connect(48 + i,
                       lambda _p=p: _p.thread.add(_p.pen_down_up))
            lp.connect(64 + i,
                       lambda _p=p: _p.thread.add(_p.c83))
            lp.connect(80 + i,
                       lambda _p=p: _p.thread.add(_p.small_line_field))
            lp.connect(96 + i,
                       lambda _p=p: _p.thread.add(_p.chatgpt_simulated_mouse_movement))

            lp.connect(112 + i, lambda _p=p: _p.thread.add(_p.next_pen))


            def clear_and_reset(pl):
                # pl.thread.clear()
                pl.thread.add(pl.reset)


            lp.connect(104 + i, lambda _p=p: clear_and_reset(_p))
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
