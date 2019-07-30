import time
import datetime
import pytz
import atexit
import os
import PySimpleGUIQt as sg
import pynput
import pyautogui
import json
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

try:
    from cursor import path
except:
    import path

json.encoder.FLOAT_REPR = lambda x: format(x, '.2f')


class InputListener:
    START_STOP_COMBINATION = {
        pynput.keyboard.Key.pause
    }
    running = True

    def __init__(self, mouse=True, keys=True):
        if mouse:
            self.mouse_listener = MouseListener(
                on_move=self.on_move,
                on_click=self.on_click)
            self.mouse_listener.start()

        if keys:
            self.key_listener = KeyboardListener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.key_listener.start()

    def toggle(self):
        if not self.running:
            print('Started')
            self.mouse_listener.start()
        else:
            print('Stopped')
            self.mouse_listener.stop()
        self.running = not self.running


class SystemTray:
    def __init__(self):
        menu_def = ['BLANK', ['&Open', '---', 'E&xit', 'Save']]
        self.tray = sg.SystemTray(menu=menu_def, filename=r'mouse-icon.gif')

    def read(self):
        return self.tray.Read(timeout=0.1)


class CursorRecorder(InputListener):
    SAVE_PATH = 'data/recordings/'
    keyboard_recodings = []
    current_line = path.Path()
    started = False
    start_time_stamp = None
    current = set()

    def __init__(self):
        super(CursorRecorder, self).__init__()
        self.start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)
        self.mouse_recordings = path.PathCollection(pyautogui.size())

        tray = SystemTray()

        print('Running recorder.. Saving to ' + self.SAVE_PATH)

        while True:
            try:
                time.sleep(0.001)
                menu_item = tray.read()
                if menu_item == 'Exit':
                    break
                elif menu_item == 'Open':
                    sg.Popup('Menu item chosen', menu_item)
                elif menu_item == 'Save':
                    self.save()
            except KeyboardInterrupt as e:
                self.save()
                return

    @staticmethod
    def _get_utc_timestamp():
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    def on_move(self, x, y):
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
        # in case this is a list of keys, for a combination
        if btn in self.START_STOP_COMBINATION:
            self.current.add(btn)
            if all(k in self.current for k in self.START_STOP_COMBINATION):
                self.toggle()

    def on_release(self, btn):
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
        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)

        recs = {'mouse': self.mouse_recordings,
                'keys': self.keyboard_recodings
                }

        fname = self.SAVE_PATH + str(self.start_time_stamp) + '.json'
        with open(fname, 'w') as fp:
            dump = json.dumps(recs, cls=path.MyJsonEncoder)
            fp.write(dump)


if __name__ == "__main__":
    rec = CursorRecorder()
