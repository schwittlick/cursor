import threading
import time

import rtmidi
import wasabi
from rtmidi.midiutil import open_midiinput

logger = wasabi.Printer(pretty=True, no_print=False)


class MidiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cbs = {}

        ports = rtmidi.MidiIn().get_ports()
        print(ports)
        for i in range(len(ports)):
            if "Midique" in ports[i]:
                logger.info(f"Detected Midique")
                self.midiin, self.port_name = open_midiinput(i)
                self.running = True
                return

        logger.fail(f"Failed to detect Midique")
        self.running = False

    def run(self):
        timer = time.time()
        prev_msg = None

        while True:
            time.sleep(0.01)

            if not self.running:
                logger.info(f"Stopping Midique Launchpad thread")
                return

            msg = self.midiin.get_message()

            if msg:
                message, deltatime = msg
                timer += deltatime

                if prev_msg is not None:
                    # TODO: why check delay?
                    if deltatime < 0.01:
                        #print(message)
                        buttonid = message[1]
                        b1 = message[2].to_bytes(1, byteorder='big')
                        b2 = prev_msg[2].to_bytes(2, byteorder='big')
                        con = b2 + b1
                        v = int.from_bytes(con, 'big')
                        norm = v / 32636 * 1000
                        if buttonid in self.cbs.keys():
                            logger.info(f"v: {norm}")
                            self.cbs[buttonid](norm)
                    else:
                        pass

                prev_msg = message

    def stop(self):
        if not self.running:
            return

        self.running = False
        self.join()
        self.midiin.close_port()
        del self.midiin


class Midique:
    def __init__(self):
        self.thread = None
        self.cbs = {}

    def connect(self, buttonid, cb):
        self.cbs[buttonid] = cb

    def stop(self):
        self.thread.stop()

    def listen(self):
        self.thread = MidiThread()
        self.thread.cbs = self.cbs
        self.thread.start()


if __name__ == '__main__':
    lp = Midique()
    lp.listen()
    # lp.close()
