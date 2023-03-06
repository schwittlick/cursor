from cursor.timer import Timer
from tools.octet.launchpad_wrapper import NovationLaunchpad

from tools.octet.plotter import Plotter
import wasabi
import time

logger = wasabi.Printer(pretty=True, no_print=False)

CONFIG = [["/dev/ttyUSB1", "9600", "500"],
          ["/dev/ttyUSB2", "9600", "500"],
          ["/dev/ttyUSB3", "9600", "500"],
          ["/dev/ttyUSB4", "9600", "500"],
          ["/dev/ttyUSB5", "9600", "500"],
          ["/dev/ttyUSB6", "9600", "500"],
          ["/dev/ttyUSB7", "9600", "500"],
          ["/dev/ttyUSB8", "9600", "500"]]


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
            if button[0] == 0 and button[1] == 0:
                logger.fail("RESET Novation")
                for i in range(8):
                    for j in range(8):
                        lp.lp.LedCtrlXY(i, j, 0, 0)
                continue

            p = plotters[button[0]]

            if button[2]:
                lp.lp.LedCtrlXY(button[0], button[1], 1, 1)
            else:
                # TODO: this should check for serial.is_open() on server side
                # add a protocol entry to server.py: IS_OPEN
                if p.is_open_serial():
                    p.close_serial()
                    success, data = p.recv()
                    logger.info(success, data)
                    if success:
                        lp.lp.LedCtrlXY(button[0], button[1], 0, 0)
                    else:
                        lp.lp.LedCtrlXY(button[0], button[1], 1, 1)
                else:
                    p.open_serial()
                    success, data = p.recv()
                    logger.info(success, data)
                    if success:
                        lp.lp.LedCtrlXY(button[0], button[1], 1, 1)
                    else:
                        lp.lp.LedCtrlXY(button[0], button[1], 0, 0)

    timer.print_elapsed("end")

    # p1.disconnect()
