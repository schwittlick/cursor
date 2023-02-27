#!/usr/bin/env python
#
# midiin_poll.py
#
"""Show how to receive MIDI input by polling an input port."""

from __future__ import print_function

import logging
import sys
import time

from rtmidi.midiutil import open_midiinput


prev_msg = None

log = logging.getLogger('midiin_poll')
logging.basicConfig(level=logging.DEBUG)

# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiin, port_name = open_midiinput(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Entering main loop. Press Control-C to exit.")
try:
    timer = time.time()
    while True:
        msg = midiin.get_message()

        if msg:
            message, deltatime = msg
            timer += deltatime

            if prev_msg is not None:
                if deltatime < 0.01:
                    #print("second msg:" + str(message[2]))
                    #print(f"{message[2]} {prev_msg[2]}")
                    print(f"{bin(prev_msg[2])} {bin(message[2])}")
                    b1 = message[2].to_bytes(1, byteorder='big')
                    b2 = prev_msg[2].to_bytes(2, byteorder='big')
                    con = b2 + b1
                    v = int.from_bytes(con, 'big')
                    norm = v/32636 * 1000
                    #print(f"{b1} {b2} {norm}")
                    print(f"{norm}")
                    #print(f"value: {prev_msg[2] * message[2]}")
                else:
                    pass
                    #print(f"first msg {message[2]}")

            prev_msg = message
            #print("[%s] @%0.6f %r" % (port_name, timer, message))

        time.sleep(0.01)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin