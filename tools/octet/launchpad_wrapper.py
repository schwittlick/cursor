import sys
import time
import wasabi

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
