from cursor import path
from cursor import data

import datetime
import pytz
import atexit
import os
import pyautogui
import wasabi
import pathlib
import pystray
import pynput
from PIL import Image

log = wasabi.Printer()


class Recorder:
    keyboard_recodings = []
    current_line = path.Path()
    started = False
    start_time_stamp = None
    recorder = None
    running = True
    size = pyautogui.size()

    def __init__(self):
        self.start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)
        self.mouse_recordings = path.PathCollection()

        log.good("Setting up mouse hook")
        self.mouse_listener = pynput.mouse.Listener(
            on_move=self.on_move, on_click=self.on_click
        )
        self.mouse_listener.start()

        log.good("Setting up keyboard hook")
        self.key_listener = pynput.keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.key_listener.start()

        log.good("Started cursor recorder")

    @staticmethod
    def _get_utc_timestamp():
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    def on_move(self, x, y):
        _x = x / self.size[0]
        _y = y / self.size[1]
        self.current_line.add(_x, _y, self._get_utc_timestamp())

    def on_click(self, x, y, button, pressed):
        if not self.started and pressed:
            _x = x / self.size[0]
            _y = y / self.size[1]
            self.current_line.add(_x, _y, self._get_utc_timestamp())
            self.started = True
        elif self.started and pressed:
            self.mouse_recordings.add(self.current_line.copy())
            global counter, icon
            counter = f"mouse: {len(self.mouse_recordings)} keys: {len(self.keyboard_recodings)}"
            icon.update_menu()
            self.current_line.clear()

    def on_press(self, btn):
        pass

    def on_release(self, btn):
        try:
            key = btn.char
        except AttributeError as ae:
            log.fail(f"Couldn't save key because of {ae}")
            return

        self.keyboard_recodings.append((key, self._get_utc_timestamp()))

    def save(self):
        save_path = data.DataPathHandler().recordings()
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


rr = None
counter = ""
icon = None


def save_exit(icon, item):
    icon.stop()


def recorder_setup(icon):
    global rr
    rr = Recorder()
    icon.visible = True


def update(icon):
    icon.update_menu()


def main(args=None):
    # the main recorder entry point
    # 1. creates a gui
    # 2. starts the recorder
    # loops forever until quit forcefully or via gui

    icon_path = (
        pathlib.Path(__file__).resolve().parent.parent.joinpath("mouse-icon.gif")
    )
    image = Image.open(icon_path.as_posix())
    global icon
    icon = pystray.Icon(
        "Cursor",
        image,
        menu=pystray.Menu(
            pystray.MenuItem(lambda text: counter, update),
            pystray.MenuItem("Save & Exit", save_exit),
        ),
    )
    log.info("Created menu")
    icon.run(recorder_setup)


if __name__ == "__main__":
    main()
