from cursor import path
from cursor import data

import datetime
import pytz
import atexit
import pyautogui
import wasabi
import pathlib
import pystray
import pynput
from PIL import Image

log = wasabi.Printer()


class Recorder:
    _mouse_recordings = path.PathCollection()
    _keyboard_recodings = []
    _current_line = path.Path()
    _started = False
    _start_time_stamp = None
    _resolution = pyautogui.size()

    def __init__(self):
        self._start_time_stamp = self._get_utc_timestamp()
        atexit.register(self.save)

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
        _x = x / self._resolution[0]
        _y = y / self._resolution[1]
        self._current_line.add(_x, _y, self._get_utc_timestamp())

    def on_click(self, x, y, button, pressed):
        if not self._started and pressed:
            _x = x / self._resolution[0]
            _y = y / self._resolution[1]
            self._current_line.add(_x, _y, self._get_utc_timestamp())
            self._started = True
        elif self._started and pressed:
            self._mouse_recordings.add(self._current_line.copy())
            global counter, icon
            counter = f"mouse: {len(self._mouse_recordings)} keys: {len(self._keyboard_recodings)}"
            icon.update_menu()
            self._current_line.clear()

    def on_press(self, btn):
        pass

    def on_release(self, btn):
        try:
            key = btn.char
        except AttributeError as ae:
            log.fail(f"Couldn't save key because of {ae}")
            return

        self._keyboard_recodings.append((key, self._get_utc_timestamp()))

    def save(self):
        save_path = data.DataDirHandler().recordings()
        save_path.mkdir(parents=True, exist_ok=True)

        recs = {"mouse": self._mouse_recordings, "keys": self._keyboard_recodings}

        fname_compressed = save_path.joinpath(str(self._start_time_stamp) + "_compressed.json")

        log.good(f"Saving mouse recordings: {len(self._mouse_recordings)}")
        log.good(f"Saving keyboard recordings: {len(self._keyboard_recodings)}")
        log.good(f"Saving compressed to {fname_compressed.as_posix()}")

        with open(fname_compressed.as_posix(), "w") as fp:
            dump = data.JsonCompressor().json_zip(recs)
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
