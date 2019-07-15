import time
import datetime
import json
import pytz
import atexit
import os
import PySimpleGUIQt as sg
from pynput.mouse import Listener as MouseListener
from interrupt_handler import GracefulInterruptHandler


class CursorRecorder(object):
    recordings = []
    current_line = []
    started = False
    start_time_stamp = None
    SAVE_PATH = 'data/recordings/'

    def _get_utc_timestamp(self):
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    def __init__(self):
        self.start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)

        mouse_listener = MouseListener(
                on_move=self.on_move,
                on_click=self.on_click)
        mouse_listener.start()

        menu_def = ['BLANK', ['&Open', '---', 'E&xit']]
        tray = sg.SystemTray(menu=menu_def, filename=r'mouse-icon.gif')

        print('Running recorder.. Saving to ' + self.SAVE_PATH)

        while True:
            menu_item = tray.Read()
            print(menu_item)
            if menu_item == 'Exit':
                break
            elif menu_item == 'Open':
                sg.Popup('Menu item chosen', menu_item)

    def on_move(self, x, y):
        self.current_line.append((x, y, self._get_utc_timestamp()))

    def on_click(self, x, y, button, pressed):
        if not self.started and pressed:
            self.current_line.append((x, y, self._get_utc_timestamp()))
            self.started = True
        elif self.started and pressed:
            self.recordings.append(self.current_line.copy())
            self.current_line.clear()

    def save(self):
        print('save')
        fname = self.SAVE_PATH + str(self.start_time_stamp) + '.json'

        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)

        with open(fname, 'w') as fp:
            print(len(self.recordings))
            json.dump(self.recordings, fp=fp)


if __name__ == "__main__":
    rec = CursorRecorder()
