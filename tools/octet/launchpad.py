import threading
import time

import rtmidi.midiutil
import wasabi
from rtmidi.midiutil import open_midiinput

logger = wasabi.Printer(pretty=True, no_print=False)


class LaunchpadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cbs = {}

        ports = rtmidi.MidiIn().get_ports()
        for i in range(len(ports)):
            if "Launchpad" in ports[i]:
                logger.info("Detected Novation Launchpad")
                self.midiin, self.port_name = open_midiinput(i)
                self.running = True
                return

        logger.fail("Failed to detect Novation Launchpad")
        self.running = False

    def run(self):
        while True:
            time.sleep(0.01)

            if not self.running:
                logger.info("Stopping Novation Launchpad thread")
                return

            msg = self.midiin.get_message()

            if msg:
                message, deltatime = msg

                print(message)
                buttonid = message[1]
                if message[2] == 127:
                    # button up
                    continue
                if buttonid in self.cbs.keys():
                    self.cbs[buttonid]()

    def stop(self):
        if not self.running:
            return

        self.running = False
        self.join()
        self.midiin.close_port()
        del self.midiin


class NovationLaunchpad:
    def __init__(self):
        self.thread = None
        self.cbs = {}

    def connect(self, buttonid, cb):
        self.cbs[buttonid] = cb

    def listen(self):
        self.thread = LaunchpadThread()
        self.thread.cbs = self.cbs
        self.thread.start()

    def reset(self):
        logger.warn("todo: RESET Novation")

    def stop(self):
        self.thread.stop()


if __name__ == '__main__':
    lp = NovationLaunchpad()
    lp.listen()
    # lp.close()
