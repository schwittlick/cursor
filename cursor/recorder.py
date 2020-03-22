from cursor import path
from cursor import data

import time
import datetime
import pytz
import atexit
import os
import pyautogui
import wasabi
import pathlib
import pystray
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

log = wasabi.Printer()


class CursorRecorder:
    keyboard_recodings = []
    current_line = path.Path()
    started = False
    start_time_stamp = None
    recorder = None
    running = True

    def __init__(self):
        self.start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)
        self.mouse_recordings = path.PathCollection(pyautogui.size())

        log.good("Setting up mouse hook")
        self.mouse_listener = MouseListener(
            on_move=self.on_move, on_click=self.on_click
        )
        self.mouse_listener.start()

        log.good("Setting up keyboard hook")
        self.key_listener = KeyboardListener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.key_listener.start()

        log.good("Started cursor recorder")

        #while True:
        #    time.sleep(0.01)

    def toggle(self):
        if not self.running:
            print("Started")
            self.mouse_listener.start()
        else:
            print("Stopped")
            self.mouse_listener.stop()
        self.running = not self.running

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
            self.mouse_recordings.add(
                self.current_line.copy(), self.mouse_recordings.resolution
            )
            self.current_line.clear()

    def on_press(self, btn):
        pass

    def on_release(self, btn):
        try:
            self.keyboard_recodings.append((btn.char, self._get_utc_timestamp()))
        except AttributeError as ae:
            log.fail(f"Couldn't save key because of {ae}")

    def save(self):
        save_path = data.DataHandler().recordings()
        pathlib.Path(save_path).mkdir(parents=True, exist_ok=True)

        recs = {"mouse": self.mouse_recordings, "keys": self.keyboard_recodings}

        fname_compressed = os.path.join(
            save_path, str(self.start_time_stamp) + "_compressed.json"
        )
        log.good(f"Saving mouse recordings: {len(self.mouse_recordings)}")
        log.good(f"Saving keyboard recordings: {len(self.keyboard_recodings)}")
        log.good(f"Saving compressed to {fname_compressed}")

        with open(fname_compressed, "w") as fp:
            dump = path.JsonCompressor().json_zip(recs)
            fp.write(str(dump))

        # fname_uncompressed = os.path.join(self.SAVE_PATH, str(self.start_time_stamp) + '_uncompressed.json')
        # with open(fname_uncompressed, 'w') as fp:
        #    dump = json.dumps(recs, cls=path.MyJsonEncoder)
        #     fp.write(dump)


from PIL import Image
rr = None

def load_image():
    im = Image.open("mouse-icon.gif")
    return im

def clicked(icon, item):
    global rr
    icon.stop()

def after(icon):
    global rr
    rr = CursorRecorder()
    icon.visible = True


def create_menu():
    image = load_image()
    icon = pystray.Icon(
        "Cursor", image, menu=pystray.Menu(pystray.MenuItem("Stop", clicked))
    )
    log.info("created menu")
    icon.run(after)

def runRecorder():
    create_menu()
    #
