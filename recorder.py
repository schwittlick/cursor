import time
import datetime
import json
import pytz
import atexit
import os
import jsonpickle
import PySimpleGUIQt as sg
import pynput
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from interrupt_handler import GracefulInterruptHandler

import path


class InputListener(object):
    START_STOP_COMBINATION = {
        pynput.keyboard.Key.pause
    }
    running = False

    def __init__(self, mouse=True, keys=True):
        if mouse:
            self.mouse_listener = MouseListener(
                on_move=self.on_move,
                on_click=self.on_click)

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


class SystemTray(object):
    def __init__(self):
        menu_def = ['BLANK', ['&Open', '---', 'E&xit', 'Save']]
        self.tray = sg.SystemTray(menu=menu_def, filename=r'mouse-icon.gif')

    def read(self):
        return self.tray.Read()


class CursorRecorder(InputListener):
    SAVE_PATH = 'data/recordings/'
    mouse_recordings = []
    keyboard_recodings = []
    current_line = path.Path()
    started = False
    start_time_stamp = None
    current = set()

    def _get_utc_timestamp(self):
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    def __init__(self):
        super(CursorRecorder, self).__init__()
        self.start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)

        tray = SystemTray()

        print('Running recorder.. Saving to ' + self.SAVE_PATH)

        while True:
            menu_item = tray.read()
            print(menu_item)
            if menu_item == 'Exit':
                break
            elif menu_item == 'Open':
                sg.Popup('Menu item chosen', menu_item)
            elif menu_item == 'Save':
                self.save()

    def on_move(self, x, y):
        self.current_line.add(x, y, self._get_utc_timestamp())

    def on_click(self, x, y, button, pressed):
        if not self.started and pressed:
            self.current_line.add(x, y, self._get_utc_timestamp())
            self.started = True
        elif self.started and pressed:
            self.mouse_recordings.append(self.current_line.copy())
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

        recs = {'mouse': self.mouse_recordings, 'keys': self.keyboard_recodings}

        fname = self.SAVE_PATH + str(self.start_time_stamp) + '.json'
        with open(fname, 'w') as fp:
            j = jsonpickle.encode(recs)
            fp.write(j)
            #json.dump(recs, fp=fp)


if __name__ == "__main__":
    rec = CursorRecorder()
