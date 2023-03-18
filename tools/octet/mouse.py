import sys
import threading

# uses the package python-xlib
# from http://snipplr.com/view/19188/mouseposition-on-linux-via-xlib/
# or: sudo apt-get install python-xlib
from time import sleep

from Xlib import display


def mousepos():
    """mousepos() --> (x, y) get the mouse coordinates on the screen (linux, Xlib)."""
    data = display.Display().screen().root.query_pointer()._data
    return data["root_x"], data["root_y"]


class MouseThread(threading.Thread):
    def __init__(self, cb):
        threading.Thread.__init__(self)
        self.killed = False
        self.cb = cb
        self._prev_mp = (0,0)

    def run(self):
        try:
            while True:
                if self.stopped():
                    break
                mp = mousepos()
                if mp == self._prev_mp:
                    continue
                text = "{0}".format(mp)
                self.cb(mp)
                print(text)
                sleep(0.01)
                self._prev_mp = mp
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

    def kill(self):
        self.killed = True

    def stopped(self):
        return self.killed

if __name__ == '__main__':
    mouseThread = MouseThread(lambda p: print(p))
    mouseThread.start()