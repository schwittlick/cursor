import threading
import time

import rtmidi
import wasabi
from rtmidi.midiutil import open_midiinput

logger = wasabi.Printer(pretty=True, no_print=False)


class MidiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        ports = rtmidi.MidiIn().get_ports()
        for i in range(len(ports)):
            if "Midique" in ports[i]:
                self.midiin, self.port_name = open_midiinput(i)
        self.cbs = {}

    def run(self):
        timer = time.time()
        prev_msg = None

        while True:
            time.sleep(0.01)

            if not self.running:
                logger.info("Midique thread finished")
                return

            if not self.midiin:
                logger.info(f"Midique thread finished midi connection dead")
                return
            msg = self.midiin.get_message()

            if msg:
                message, deltatime = msg
                timer += deltatime

                if prev_msg is not None:
                    # TODO: why check delay?
                    if deltatime < 0.01:
                        # print("wtf")
                        print(message)
                        buttonid = message[1]
                        if buttonid == 32:
                            # end thread
                            return
                        # print("second msg:" + str(message[2]))
                        # print(f"{message[2]} {prev_msg[2]}")
                        # print(f"{bin(prev_msg[2])} {bin(message[2])}")
                        b1 = message[2].to_bytes(1, byteorder='big')
                        b2 = prev_msg[2].to_bytes(2, byteorder='big')
                        con = b2 + b1
                        v = int.from_bytes(con, 'big')
                        norm = v / 32636 * 1000
                        # print(f"{b1} {b2} {norm}")
                        print(f"{norm}")
                        if buttonid in self.cbs.keys():
                            logger.info(f"running cb {self.cbs[buttonid]}")
                            self.cbs[buttonid](norm)
                        # print(f"value: {prev_msg[2] * message[2]}")
                    else:
                        pass
                        # print(f"first msg {message[2]}")

                prev_msg = message
                # print("[%s] @%0.6f %r" % (port_name, timer, message))

    def stop(self):
        self.running = False
        logger.info("Exit Midique thread.")
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
