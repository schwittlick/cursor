from cursor.misc import Timer
from tools.octet.launchpad_wrapper import NovationLaunchpad

from tools.octet.plotter import Plotter
import wasabi
import time

logger = wasabi.Printer(pretty=True, no_print=False)

CONFIG = [["COM1", "9600", "500"],
          ["COM2", "9600", "500"],
          ["COM3", "9600", "500"],
          ["COM4", "9600", "500"],
          ["COM5", "9600", "500"],
          ["COM6", "9600", "500"],
          ["COM7", "9600", "500"],
          ["COM8", "9600", "500"]]


def log(tup):
    success, msg = tup
    if success:
        logger.good(msg)
    else:
        logger.fail(msg)


if __name__ == '__main__':
    lp = NovationLaunchpad()

    plotters = []
    for cfg in CONFIG:
        p = Plotter(cfg[0], int(cfg[1]), int(cfg[2]))
        p.connect()
        plotters.append(p)

    timer = Timer()
    while True:
        time.sleep(0.001)
        CONNECT_Y = 1

        button = lp.poll()
        if button != []:
            print(button)
            p = plotters[0]
            if button[0] == 0 and button[1] == 1 and button[2]:
                lp.lp.LedCtrlXY(button[0], button[1], 1, 1)
            if button[0] == 0 and button[1] == 1 and not button[2]:
                p.open_serial()
                success, data = p.recv()
                print(success)
                if success:
                    lp.lp.LedCtrlXY(button[0], button[1], 1, 1)
                else:
                    lp.lp.LedCtrlXY(button[0], button[1], 0, 0)

    timer.print_elapsed("end")

    # p1.disconnect()
