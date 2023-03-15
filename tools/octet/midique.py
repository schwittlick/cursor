import sys
import time
from threading import Thread

import wasabi
from rtmidi.midiutil import open_midiinput

logger = wasabi.Printer(pretty=True, no_print=False)


class Midique:
    def __init__(self, port):
        try:
            self.midiin, self.port_name = open_midiinput(port)
        except (EOFError, KeyboardInterrupt):
            sys.exit()

        self.cbs = {}

    def connect(self, buttonid, cb):
        self.cbs[buttonid] = cb

    def listen(self):

        def func():
            if not self.midiin:
                logger.warn("not starting.. not open")
            print("Entering main loop. Press Control-C to exit.")
            try:
                timer = time.time()
                prev_msg = None

                while True:
                    msg = self.midiin.get_message()

                    if msg:
                        message, deltatime = msg
                        timer += deltatime

                        if prev_msg is not None:
                            if deltatime < 0.01:
                                print("wtf")
                                print(message)
                                buttonid = message[1]
                                if buttonid == 32:
                                    # end thread
                                    return
                                # print("second msg:" + str(message[2]))
                                # print(f"{message[2]} {prev_msg[2]}")
                                print(f"{bin(prev_msg[2])} {bin(message[2])}")
                                b1 = message[2].to_bytes(1, byteorder='big')
                                b2 = prev_msg[2].to_bytes(2, byteorder='big')
                                con = b2 + b1
                                v = int.from_bytes(con, 'big')
                                norm = v / 32636 * 1000
                                # print(f"{b1} {b2} {norm}")
                                print(f"{norm}")
                                if buttonid in self.cbs.keys():
                                    self.cbs[buttonid](norm)
                                # print(f"value: {prev_msg[2] * message[2]}")
                            else:
                                pass
                                # print(f"first msg {message[2]}")

                        prev_msg = message
                        # print("[%s] @%0.6f %r" % (port_name, timer, message))

                    time.sleep(0.01)
            except KeyboardInterrupt:
                print('')
            finally:
                print("Exit.")
                self.midiin.close_port()
                del self.midiin

        thread = Thread(target=func)
        thread.start()
