#!/usr/bin/env python
#
# midiin_callback.py
#
"""Show how to receive MIDI input by setting a callback function."""

from __future__ import print_function

import logging
import sys
import time

from rtmidi.midiutil import open_midiinput

global prev_msg
prev_msg = None

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)


def messages_to_int(prev, curr, resolution=600) -> int:
    b1 = curr[2].to_bytes(1, byteorder='big')
    b2 = prev[2].to_bytes(2, byteorder='big')
    con = b2 + b1
    v = int.from_bytes(con, 'big')
    norm = v / 32636 * resolution
    # 32636 = max value from kntrl9
    return int(norm)


class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        global prev_msg
        message, deltatime = event
        if prev_msg is not None:
            if deltatime < 0.01:
                v = messages_to_int(prev_msg, message)
                print(f"{v} {message[1]-32}")

        prev_msg = message
        self._wallclock += deltatime
        #print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))


# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(port_name))

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin
