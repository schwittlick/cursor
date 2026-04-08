import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import threading
from typing import Optional

import evdev
from evdev import ecodes

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.load.compress import JsonCompressor
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property
from cursor.timer import DateHandler

# Maps evdev key codes to the string representation used in recordings.
# Printable characters fall through to the generic handler at the bottom.
_KEY_MAP: dict[int, str] = {
    ecodes.KEY_SPACE: " ",
    ecodes.KEY_DELETE: "DEL",
    ecodes.KEY_LEFTMETA: "CMD_L",
    ecodes.KEY_RIGHTMETA: "CMD_R",
    ecodes.KEY_LEFTALT: "ALT_L",
    ecodes.KEY_RIGHTALT: "ALT_R",
    ecodes.KEY_ENTER: "ENTER",
    ecodes.KEY_BACKSPACE: "BACKSPACE",
    ecodes.KEY_LEFTSHIFT: "SHIFT_L",
    ecodes.KEY_RIGHTSHIFT: "SHIFT_R",
    ecodes.KEY_LEFTCTRL: "CTRL_L",
    ecodes.KEY_RIGHTCTRL: "CTRL_R",
    ecodes.KEY_TAB: "TAB",
}


def _keycode_to_str(code: int) -> Optional[str]:
    if code in _KEY_MAP:
        return _KEY_MAP[code]
    # ecodes.KEY is a dict mapping code -> name string, e.g. "KEY_A"
    name = ecodes.KEY.get(code)
    if name is None:
        return None
    # "KEY_A" → "a", "KEY_1" → "1"
    if isinstance(name, list):
        name = name[0]
    suffix = name.removeprefix("KEY_")
    if len(suffix) == 1:
        return suffix.lower()
    return None


def find_mouse_devices() -> list[evdev.InputDevice]:
    devices = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities()
            has_rel = ecodes.EV_REL in caps
            has_btn = ecodes.EV_KEY in caps and ecodes.BTN_LEFT in caps[ecodes.EV_KEY]
            if has_rel and has_btn:
                devices.append(dev)
        except Exception:
            pass
    return devices


def find_keyboard_devices() -> list[evdev.InputDevice]:
    devices = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
            caps = dev.capabilities()
            is_kbd = ecodes.EV_KEY in caps and ecodes.KEY_A in caps[ecodes.EV_KEY]
            if is_kbd:
                devices.append(dev)
        except Exception:
            pass
    return devices


def _get_cursor_pos() -> tuple[float, float]:
    out = subprocess.check_output(["hyprctl", "cursorpos"], text=True).strip()
    # format: "x, y"
    x_str, y_str = out.split(",")
    return float(x_str.strip()), float(y_str.strip())


def _get_monitor_resolution() -> tuple[int, int]:
    out = subprocess.check_output(["hyprctl", "monitors", "-j"], text=True)
    monitors = json.loads(out)
    # use the first (primary) monitor
    m = monitors[0]
    return m["width"], m["height"]


def _sample_color_at(x: float, y: float) -> tuple[int, int, int]:
    """Capture a 1x1 pixel at screen coordinates (x, y) via grim."""
    try:
        import os
        import tempfile

        from PIL import Image

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tmp = f.name
        subprocess.run(
            ["grim", "-g", f"{int(x)},{int(y)} 1x1", tmp],
            check=True,
            capture_output=True,
        )
        with Image.open(tmp) as img:
            r, g, b = img.getpixel((0, 0))[:3]
        os.unlink(tmp)
        return (r, g, b)
    except Exception:
        return (0, 0, 0)


class RecorderWayland:
    def __init__(self, suffix: str, sample_color: bool = False) -> None:
        self._fn_suffix = suffix
        self._sample_color = sample_color

        self._lock = threading.Lock()
        self._mouse_recordings = Collection()
        self._keyboard_recordings: list[tuple] = []
        self._current_line = Path()
        self._started = False
        self._start_time_stamp = DateHandler.utc_timestamp()
        self._timer: Optional[threading.Timer] = None

        cx, cy = _get_cursor_pos()
        self._cx = cx
        self._cy = cy
        self._res_w, self._res_h = _get_monitor_resolution()

        log.info(f"Screen resolution: {self._res_w}x{self._res_h}")
        log.info(f"Initial cursor position: {self._cx}, {self._cy}")

        mouse_devs = find_mouse_devices()
        kbd_devs = find_keyboard_devices()

        if not mouse_devs:
            log.error("No mouse devices found. Check /dev/input permissions (input group).")
        if not kbd_devs:
            log.error("No keyboard devices found.")

        for dev in mouse_devs:
            log.info(f"Mouse device: {dev.name} ({dev.path})")
            t = threading.Thread(target=self._mouse_thread, args=(dev,), daemon=True)
            t.start()

        for dev in kbd_devs:
            log.info(f"Keyboard device: {dev.name} ({dev.path})")
            t = threading.Thread(target=self._keyboard_thread, args=(dev,), daemon=True)
            t.start()

        self.__save_async()

        subprocess.run(
            ["notify-send", "Cursor Recorder", f"Started — suffix: {suffix}\nPID: {os.getpid()}"],
            capture_output=True,
        )
        log.info(f"Started cursor recorder (PID {os.getpid()}). Ctrl+C or SIGINT to stop.")

    def stop(self) -> None:
        if self._timer:
            self._timer.cancel()
        self.save()

    def __save_async(self) -> None:
        self.save()
        log.info("Setting up 30min auto-save")
        self._timer = threading.Timer(60 * 30, self.__save_async)
        self._timer.daemon = True
        self._timer.start()

    # ------------------------------------------------------------------
    # Mouse tracking
    # ------------------------------------------------------------------

    def _mouse_thread(self, device: evdev.InputDevice) -> None:
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_REL:
                    with self._lock:
                        if event.code == ecodes.REL_X:
                            self._cx = max(0.0, min(self._cx + event.value, self._res_w - 1))
                        elif event.code == ecodes.REL_Y:
                            self._cy = max(0.0, min(self._cy + event.value, self._res_h - 1))
                        self._on_move()
                elif event.type == ecodes.EV_KEY and event.code == ecodes.BTN_LEFT:
                    with self._lock:
                        self._on_click(pressed=event.value == 1)
        except Exception as e:
            log.error(f"Mouse thread error: {e}")

    def _on_move(self) -> None:
        """Called with self._lock held."""
        _x = self._cx / self._res_w
        _y = self._cy / self._res_h
        _t = int(DateHandler.utc_timestamp())
        _p = Position(_x, _y, _t, {Property.COLOR: (0, 0, 0)})
        self._current_line.add_position(_p)

    def _on_click(self, pressed: bool) -> None:
        """Called with self._lock held."""
        if not self._started and pressed:
            self._on_move()
            self._started = True
            return

        if self._started and pressed:
            if self._sample_color:
                color = _sample_color_at(self._cx, self._cy)
                for pos in self._current_line.vertices:
                    pos.properties[Property.COLOR] = color

            self._mouse_recordings.add(self._current_line.copy())
            self._current_line.clear()
            mouse_count = len(self._mouse_recordings)
            kbd_count = len(self._keyboard_recordings)
            log.info(f"mouse: {mouse_count}  keys: {kbd_count}")
            subprocess.Popen(
                ["notify-send", "-t", "2000", "Cursor Recorder", f"mouse: {mouse_count}  keys: {kbd_count}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    # ------------------------------------------------------------------
    # Keyboard tracking
    # ------------------------------------------------------------------

    def _keyboard_thread(self, device: evdev.InputDevice) -> None:
        try:
            for event in device.read_loop():
                if event.type != ecodes.EV_KEY:
                    continue
                # value: 1=press, 0=release, 2=repeat
                if event.value == 1:
                    self._on_key(event.code, down=True)
                elif event.value == 0:
                    self._on_key(event.code, down=False)
        except Exception as e:
            log.error(f"Keyboard thread error: {e}")

    def _on_key(self, code: int, down: bool) -> None:
        key = _keycode_to_str(code)
        if key is None:
            return
        t = (key, DateHandler.utc_timestamp(), 1 if down else 0)
        with self._lock:
            self._keyboard_recordings.append(t)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> None:
        save_path = DataDirHandler().recordings()
        save_path.mkdir(parents=True, exist_ok=True)

        with self._lock:
            recs = {
                "mouse": self._mouse_recordings,
                "keys": list(self._keyboard_recordings),
            }
            mouse_count = len(self._mouse_recordings)
            kbd_count = len(self._keyboard_recordings)

        filename = str(self._start_time_stamp) + f"_{self._fn_suffix}.json"
        fpath = save_path / filename

        log.warning(DateHandler.utc_timestamp())
        log.info(f"Saving mouse recordings: {mouse_count}")
        log.info(f"Saving keyboard recordings: {kbd_count}")
        log.info(fpath.as_posix())

        with open(fpath.as_posix(), "w") as fp:
            fp.write(str(JsonCompressor().json_zip(recs)))


# Module-level recorder reference (needed for signal handlers)
_rr: Optional[RecorderWayland] = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Wayland-native cursor recorder")
    parser.add_argument("--suffix", default=None, help="Recording suffix / label")
    parser.add_argument(
        "--sample-color",
        action="store_true",
        help="Sample screen color at each click via grim (adds ~100ms per click)",
    )
    args = parser.parse_args()

    suffix = args.suffix or input("suffix: ").strip()
    if not suffix:
        sys.exit("No suffix provided.")

    global _rr

    def _stop(signum, frame):  # noqa: ARG001
        log.info("Stopping recorder…")
        if _rr:
            _rr.stop()
        sys.exit(0)

    def _manual_save(signum, frame):  # noqa: ARG001
        log.info("Manual save triggered (SIGUSR1)")
        if _rr:
            _rr.save()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGUSR1, _manual_save)

    _rr = RecorderWayland(suffix, sample_color=args.sample_color)

    # Block the main thread until a signal arrives
    stop_event = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: stop_event.set() or _stop(*_))
    stop_event.wait()


if __name__ == "__main__":
    main()
