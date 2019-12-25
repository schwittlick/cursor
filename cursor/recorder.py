import time
import datetime
import pytz
import atexit
import os
import pyautogui
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

from cursor import path
from cursor import data


class CursorRecorder:
    SAVE_PATH = data.DataHandler().recordings()
    keyboard_recodings = []
    current_line = path.Path()
    started = False
    start_time_stamp = None
    current = set()
    recorder = None
    running = True

    def __init__(self):
        print(self.SAVE_PATH)

        self.start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)
        self.mouse_recordings = path.PathCollection(pyautogui.size())

        self.mouse_listener = MouseListener(
            on_move=self.on_move,
            on_click=self.on_click)
        self.mouse_listener.start()

        self.key_listener = KeyboardListener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.key_listener.start()

        print('Running recorder.. Saving to ' + self.SAVE_PATH)

        while True:
            time.sleep(0.01)

    def toggle(self):
        if not self.running:
            print('Started')
            self.mouse_listener.start()
        else:
            print('Stopped')
            self.mouse_listener.stop()
        self.running = not self.running

    @staticmethod
    def _get_utc_timestamp():
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    def on_move(self, x, y):
        print("move " + str(x))
        _x = x / self.mouse_recordings.resolution.width
        _y = y / self.mouse_recordings.resolution.height
        self.current_line.add(_x, _y, self._get_utc_timestamp())

    def on_click(self, x, y, button, pressed):
        if not self.started and pressed:
            _x = x / self.mouse_recordings.resolution.width
            _y = y / self.mouse_recordings.resolution.height
            self.current_line.add(_x, _y, self._get_utc_timestamp())
            self.started = True
        elif self.started and pressed:
            self.mouse_recordings.add(self.current_line.copy(), self.mouse_recordings.resolution)
            self.current_line.clear()

    def on_press(self, btn):
        print("press " + str(btn))
        pass
        # in case this is a list of keys, for a combination
        # if btn in self.START_STOP_COMBINATION:
        #    self.current.add(btn)
        #    if all(k in self.current for k in self.START_STOP_COMBINATION):
        #        self.toggle()

    def on_release(self, btn):
        print("release " + str(btn))
        try:
            self.current.remove(btn)
            return
        except KeyError:
            pass
        try:
            self.keyboard_recodings.append((btn.char, self._get_utc_timestamp()))
        except AttributeError as ae:
            print(ae)

    def save(self):
        print("save")
        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)

        recs = {'mouse': self.mouse_recordings,
                'keys': self.keyboard_recodings
                }

        fname_compressed = os.path.join(self.SAVE_PATH, str(self.start_time_stamp) + '_compressed.json')
        with open(fname_compressed, 'w') as fp:
            dump = path.JsonCompressor().json_zip(recs)
            fp.write(str(dump))

        # fname_uncompressed = os.path.join(self.SAVE_PATH, str(self.start_time_stamp) + '_uncompressed.json')
        # with open(fname_uncompressed, 'w') as fp:
        #    dump = json.dumps(recs, cls=path.MyJsonEncoder)
        #     fp.write(dump)


def runRecorder():
    CursorRecorder()