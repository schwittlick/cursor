import sys
import time
import wasabi

from cursor.timer import Timer

logger = wasabi.Printer(pretty=True, no_print=False)

try:
    import launchpad_py as launchpad
except ImportError as e:
    print(e)
    try:
        import launchpad
    except ImportError as e:
        print(e)
        sys.exit("error loading launchpad.py")



USE_NOVATION = True
lp = None


def novation_poll(plotters):
    if USE_NOVATION:
        lp = NovationLaunchpad()
        reset_novation(lp)

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
                reset_novation(lp)

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


def set_novation_button(lp, data, x: int, y: int, state: bool):
    if not lp:
        return
    value = 1 if state else 0
    lp.lp.LedCtrlXY(data[x], data[y], value, value)


def reset_novation(lp):
    logger.warn("RESET Novation")
    if not lp.lp:
        return
    for i in range(8):
        for j in range(8):
            lp.lp.LedCtrlXY(i, j, 0, 0)


class NovationLaunchpad:
    def __init__(self):
        self.mode = None
        self.lp = None
        if launchpad.Launchpad().Check(0):
            self.lp = launchpad.Launchpad()
            if self.lp.Open(0):
                print("Launchpad Mk1/S/Mini")
                self.mode = "Mk1"

        if self.mode is None:
            print("Did not find any Launchpads, meh...")
            return

    def poll(self):
        buts = self.lp.ButtonStateXY()
        if buts != []:
            brightness = 2 if buts[2] else 0
            self.lp.LedCtrlXY(buts[0], buts[1], brightness, brightness)
        return buts

    def close(self):
        logger.good(f"Safely exited {self.lp}")
        self.lp.Close()


def main():
    lp = NovationLaunchpad()

    while True:
        state = lp.poll()

        time.sleep(0.001)


if __name__ == '__main__':
    main()
