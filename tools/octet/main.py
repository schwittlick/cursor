from cursor.misc import Timer

from tools.octet.plotter import Plotter
import wasabi

logger = wasabi.Printer(pretty=True, no_print=True)

CONFIG = {"COM1", 9600, 500}


def log(tup):
    success, msg = tup
    if success:
        logger.good(msg)
    else:
        logger.fail(msg)


if __name__ == '__main__':
    p1 = Plotter("COM1", 9600, 500)
    p1.connect()

    timer = Timer()
    for i in range(7000):
        p1.open_serial()
        log(p1.recv())

    timer.print_elapsed("end")

    # p1.disconnect()
