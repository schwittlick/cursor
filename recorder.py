import time
import datetime
import json
import pytz
import pyautogui
from pynput.mouse import Listener as MouseListener
from interrupt_handler import GracefulInterruptHandler


class CursorRecorder(object):

    recordings = []
    current_line = []
    started = False
    start_time_stamp = None
    SAVE_PATH = 'data/recordings/'
    SCREEN_RESOLUTION = None

    def __init__(self):
        self.start_time_stamp = self._get_utc_timestamp()
        self.SCREEN_RESOLUTION = pyautogui.size()

        mouse_listener = MouseListener(
                on_move=self.on_move,
                on_click=self.on_click)
        mouse_listener.start()

        with GracefulInterruptHandler() as h:
            while True:
                time.sleep(0.2)
                if h.interrupted:
                    self.save()
                    break

    @staticmethod
    def _get_utc_timestamp():
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    def on_move(self, x, y):
        _x = x / self.SCREEN_RESOLUTION.width
        _y = y / self.SCREEN_RESOLUTION.height
        self.current_line.append((_x, _y, self._get_utc_timestamp()))

    def on_click(self, x, y, button, pressed):
        if not self.started and pressed:
            _x = x / self.SCREEN_RESOLUTION.width
            _y = y / self.SCREEN_RESOLUTION.height

            self.current_line.append((_x, _y, self._get_utc_timestamp()))
            self.started = True
        elif self.started and pressed:
            print(len(self.current_line))
            self.recordings.append(self.current_line.copy())
            self.current_line.clear()

    def save(self):
        fname = self.SAVE_PATH + str(self.start_time_stamp) + '.json'
        with open(fname, 'w') as fp:
            print(len(self.recordings))
            json.dump(self.recordings, fp=fp)


if __name__ == "__main__":
    rec = CursorRecorder()
