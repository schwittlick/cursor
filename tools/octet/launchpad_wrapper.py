import sys
import threading
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
                set_novation_button(lp, button, 0, 1, True)
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
                            set_novation_button(lp, button, 0, 1, False)
                        else:
                            set_novation_button(lp, button, 0, 1, True)
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
                                set_novation_button(lp, button, 0, 1, True)
                            else:
                                set_novation_button(lp, button, 0, 1, False)
                        else:
                            set_novation_button(lp, button, 0, 1, False)
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
    if not lp:
        return
    for i in range(8):
        for j in range(8):
            lp.LedCtrlXY(i, j, 0, 0)



class LaunchpadThread(threading.Thread):
    def __init__(self, lp):
        threading.Thread.__init__(self)
        self.running = True
        self.lp = lp
        self.cbs = {}

    def poll(self):
        buts = self.lp.ButtonStateXY()
        if buts != []:
            brightness = 2 if buts[2] else 0
            self.lp.LedCtrlXY(buts[0], buts[1], brightness, brightness)
        return buts

    def run(self):
        while True:
            time.sleep(0.001)

            if not self.running:
                logger.info(f"Stopping Launchpad thread, Stop")
                return

            if not self.lp:
                logger.info(f"Stopping Launchpad thread, Launchpad not working")
                return

            button = self.poll()

            if button != []:
                logger.info(button)

                if button[0] == 0 and button[1] == 0:
                    reset_novation(self.lp)
                    continue


    def stop(self):
        self.running = False

class NovationLaunchpad:
    def __init__(self):
        self.mode = None
        self.lp = None
        logger.info(f"{launchpad.Launchpad().ListAll()}")
        if launchpad.Launchpad().Check(0):
            self.lp = launchpad.Launchpad()
            if self.lp.Open(0):
                logger.info("Novation Launchpad Mini")
                self.mode = "Mk1"
            else:
                logger.fail(f"Opening Launchpad failed")
        else:
            logger.fail(f"Couldn't start Launchpad")

        if self.mode is None:
            logger.fail("Did not find any Launchpads, meh...")
            return

        self.thread = LaunchpadThread(self.lp)
        self.thread.start()

    def reset(self):
        logger.warn("RESET Novation")
        if not self.lp.lp:
            return
        for i in range(8):
            for j in range(8):
                self.lp.lp.LedCtrlXY(i, j, 0, 0)

    def close(self):
        logger.good(f"Safely exited {self.lp}")
        if self.lp:
            self.lp.Close()
        self.thread.stop()


def main():
    lp = NovationLaunchpad()
    lp.close()



if __name__ == '__main__':
    main()
