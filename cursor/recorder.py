import sys

from cursor.path import Path
from cursor.collection import Collection
from cursor.data import DateHandler
from cursor.data import JsonCompressor
from cursor.data import DataDirHandler

import atexit
import pyautogui
import wasabi
import pathlib
import pystray
import pynput
import pymsgbox
import threading

from PIL import Image

log = wasabi.Printer()


class Recorder:
    def __init__(self, suffix: str):
        self._fn_suffix = suffix

        self._timer = None
        self._mouse_recordings = Collection()
        self._keyboard_recodings = []
        self._current_line = Path()
        self._started = False
        self._start_time_stamp = DateHandler.utc_timestamp()
        self._resolution = pyautogui.size()

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

        log.good("Setting up 10s auto-save")
        self.__save_async()

        log.good("Started cursor recorder")

    def stop(self):
        self._timer.cancel()

    def __save_async(self):
        self.save()
        # every 10s
        self._timer = threading.Timer(10, self.__save_async, [])
        self._timer.start()

    def on_move(self, x, y):
        _x = x / self._resolution[0]
        _y = y / self._resolution[1]
        self._current_line.add(_x, _y, int(DateHandler.utc_timestamp()))

    def on_click(self, x, y, button, pressed):
        if not self._started and pressed:
            _x = x / self._resolution[0]
            _y = y / self._resolution[1]
            self._current_line.add(_x, _y, int(DateHandler.utc_timestamp()))
            self._started = True
        elif self._started and pressed:
            self._mouse_recordings.add(self._current_line.copy())
            global status, icon
            status = f"mouse: {len(self._mouse_recordings)} keys: {len(self._keyboard_recodings)}"
            icon.update_menu()
            self._current_line.clear()

    def on_press(self, btn):
        try:
            key = btn.char
        except AttributeError as ae:
            key = self.__convert_btn_to_key(btn)
            if key is None:
                log.fail(f"Couldn't save key because of {ae}")
                return

        t = (key, DateHandler.utc_timestamp(), 1)
        log.good(t)
        self._keyboard_recodings.append(t)

    def on_release(self, btn):
        try:
            key = btn.char
        except AttributeError as ae:
            key = self.__convert_btn_to_key(btn)
            if key is None:
                log.fail(f"Couldn't save key because of {ae}")
                return

        t = (key, DateHandler.utc_timestamp(), 0)
        log.good(t)
        self._keyboard_recodings.append(t)

    def save(self):
        save_path = DataDirHandler().recordings()
        save_path.mkdir(parents=True, exist_ok=True)

        recs = {"mouse": self._mouse_recordings, "keys": self._keyboard_recodings}

        fname_compressed = save_path / (
            str(self._start_time_stamp) + f"_{self._fn_suffix}.json"
        )

        log.warn(DateHandler.utc_timestamp())
        log.good(f"Saving mouse recordings: {len(self._mouse_recordings)}")
        log.good(f"Saving keyboard recordings: {len(self._keyboard_recodings)}")
        log.good(f"{fname_compressed.as_posix()}")

        with open(fname_compressed.as_posix(), "w") as fp:
            dump = JsonCompressor().json_zip(recs)
            fp.write(str(dump))

    @staticmethod
    def __convert_btn_to_key(btn):
        """
        these keyboard keys dont have char representation
        we make it ourselves
        """
        if btn == pynput.keyboard.Key.space:
            return " "

        if btn == pynput.keyboard.Key.delete:
            return "DEL"

        if btn == pynput.keyboard.Key.cmd:
            return "CMD"

        if btn == pynput.keyboard.Key.cmd_l:
            return "CMD_L"

        if btn == pynput.keyboard.Key.cmd_r:
            return "CMD_R"

        if btn == pynput.keyboard.Key.alt:
            return "ALT"

        if btn == pynput.keyboard.Key.alt_l:
            return "ALT_L"

        if btn == pynput.keyboard.Key.alt_r:
            return "ALT_R"

        if btn == pynput.keyboard.Key.enter:
            return "ENTER"

        if btn == pynput.keyboard.Key.backspace:
            return "BACKSPACE"

        if btn == pynput.keyboard.Key.shift:
            return "SHIFT"

        if btn == pynput.keyboard.Key.shift_l:
            return "SHIFT_L"

        if btn == pynput.keyboard.Key.shift_r:
            return "SHIFT_R"

        if btn == pynput.keyboard.Key.ctrl:
            return "CTRL"

        if btn == pynput.keyboard.Key.ctrl_l:
            return "CTRL_L"

        if btn == pynput.keyboard.Key.ctrl_r:
            return "CTRL_R"

        return None


rr = None
status = ""
icon = None
suffix = ""


def save_exit(icon, item):
    global rr
    rr.stop()
    icon.stop()


def recorder_setup(icon):
    global rr

    rr = Recorder(suffix)
    icon.visible = True


def main():
    # the main recorder entry point
    # 1. creates a gui
    # 2. starts the recorder
    # loops forever until quit forcefully or via gui

    def update(icon):
        icon.update_menu()

    icon_path = pathlib.Path(__file__).resolve().parent.parent / "mouse-icon.gif"
    image = Image.open(icon_path.as_posix())
    global icon
    icon = pystray.Icon(
        "Cursor",
        image,
        menu=pystray.Menu(
            pystray.MenuItem(lambda text: status, update),
            pystray.MenuItem("Save & Exit", save_exit),
        ),
    )
    suffix = pymsgbox.prompt("suffix", default="")

    if not suffix:
        log.fail("Closing recorder, no suffix was set.")
        sys.exit()

    log.info("Created menu")
    icon.run(recorder_setup)


if __name__ == "__main__":
    main()
