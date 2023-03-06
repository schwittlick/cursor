from cursor.timer import Timer
from tools.octet.launchpad_wrapper import NovationLaunchpad

from tools.octet.plotter import Plotter
import wasabi
import time

logger = wasabi.Printer(pretty=True, no_print=False)

CONFIG = [["192.168.2.125", "12345", "/dev/ttyUSB1", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB2", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB3", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB4", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB5", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB6", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB7", "9600", "500"],
          ["192.168.2.124", "12345", "/dev/ttyUSB8", "9600", "500"]]


def log(tup):
    success, msg = tup
    if success:
        logger.good(msg)
    else:
        logger.fail(msg)


def set_novation_button(data, x: int, y: int, state: bool):
    value = 1 if state else 0
    lp.lp.LedCtrlXY(data[x], data[y], value, value)


def reset_novation():
    logger.warn("RESET Novation")
    for i in range(8):
        for j in range(8):
            lp.lp.LedCtrlXY(i, j, 0, 0)


if __name__ == '__main__':
    lp = NovationLaunchpad()
    reset_novation()

    plotters = []
    for cfg in CONFIG:
        p = Plotter(cfg[0], int(cfg[1]), cfg[2], int(cfg[3]), int(cfg[4]))
        p.connect()
        plotters.append(p)

    timer = Timer()
    while True:
        time.sleep(0.001)
        CONNECT_Y = 1

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
                    if p.is_open_serial():
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
