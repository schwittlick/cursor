import logging
import threading
import time
import typing
from enum import Enum

import rtmidi
from rtmidi.midiutil import open_midiinput

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class MidiqueKnob(Enum):
    """
    ColumnNRRowNR (e.g. C0R2)
    """
    C0R0 = 32
    C0R1 = 33
    C0R2 = 34
    C0R3 = 35

    C1R0 = 36
    C1R1 = 37
    C1R2 = 38
    C1R3 = 39

    C2R0 = 40
    C2R1 = 41
    C2R2 = 42
    C2R3 = 43

    C3R0 = 44
    C3R1 = 45
    C3R2 = 46
    C3R3 = 47

    C4R0 = 48
    C4R1 = 49
    C4R2 = 50
    C4R3 = 51

    C5R0 = 52
    C5R1 = 53
    C5R2 = 54
    C5R3 = 55

    C6R0 = 56
    C6R1 = 57
    C6R2 = 58
    C6R3 = 59

    C7R0 = 60
    C7R1 = 61
    C7R2 = 62
    C7R3 = 63

    C8R0 = 64
    C8R1 = 65
    C8R2 = 66
    C8R3 = 67


class MidiThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cbs = {}

        ports = rtmidi.MidiIn().get_ports()
        logging.debug(ports)
        for port in ports:
            if "Midique" in port:
                self.midiin, self.port_name = open_midiinput(port)
                logging.info("Detected Midique")
                self.running = True
                return

        logging.error("Failed to detect Midique")
        self.running = False

    @staticmethod
    def convert_10bit_midi_to_int(part1: int, part2: int) -> int:
        """
        also normalizes the values between 0 and 1000
        """
        concat = (part1 << 8) | part2
        norm = concat / 32636 * 1000
        return int(norm)

    def run(self) -> None:
        prev_msg = None

        while True:
            time.sleep(0.01)

            if not self.running:
                logging.info("Stopping Midique Launchpad thread")
                return

            midi_message = self.midiin.get_message()

            if midi_message:
                message, deltatime = midi_message
                logging.debug(f"{message} - {deltatime}")

                # the messages with a non-zero deltatime are the ones sent with
                # the first part of the message. quiete reliably
                if deltatime > 0.0:
                    prev_msg = message
                    continue

                if not prev_msg:
                    continue

                knob_id = message[1]
                logging.info(f"knob: {knob_id}")

                # converting 10 bit midi signal that was split over two signals
                norm = self.convert_10bit_midi_to_int(prev_msg[2], message[2])
                logging.info(f"v: {norm}")
                if knob_id in self.cbs.keys():
                    logging.info(f"v: {norm}")
                    self.cbs[knob_id](norm)

    def stop(self) -> None:
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

    def connect(self, buttonid: MidiqueKnob, cb: typing.Callable) -> None:
        self.cbs[buttonid] = cb

    def stop(self) -> None:
        self.thread.stop()

    def listen(self) -> None:
        self.thread = MidiThread()
        self.thread.cbs = self.cbs
        self.thread.start()


if __name__ == '__main__':
    lp = Midique()
    lp.listen()
    # lp.close()
