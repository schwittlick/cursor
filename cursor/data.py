from cursor.path import Path
from cursor.path import PathCollection
from cursor.path import TimedPosition

import pathlib
import json
import base64
import zlib
import pyautogui
import datetime
import pytz


class MyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PathCollection):
            return {
                "paths": o.get_all(),
                "timestamp": o.timestamp(),
            }

        if isinstance(o, Path):
            return o.vertices

        if isinstance(o, TimedPosition):
            return {"x": round(o.x, 4), "y": round(o.y, 4), "ts": round(o.timestamp, 2)}


class MyJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        from cursor.path import Path
        from cursor.path import PathCollection
        from cursor.path import TimedPosition

        if "x" in dct and "y" in dct and "ts" in dct:
            p = TimedPosition(dct["x"], dct["y"], dct["ts"])
            return p
        if "w" in dct and "h" in dct:
            s = pyautogui.Size(dct["w"], dct["h"])
            return s
        if "paths" in dct and "timestamp" in dct:
            ts = dct["timestamp"]
            pc = PathCollection(ts)
            for p in dct["paths"]:
                pc.add(Path(p))
            return pc
        return dct


class JsonCompressor:
    ZIPJSON_KEY = "base64(zip(o))"

    def json_zip(self, j):
        dumped = json.dumps(j, cls=MyJsonEncoder)
        dumped_encoded = dumped.encode("utf-8")
        compressed = zlib.compress(dumped_encoded)
        encoded = {self.ZIPJSON_KEY: base64.b64encode(compressed).decode("ascii")}

        return encoded

    def json_unzip(self, j, insist=True):
        try:
            assert j[self.ZIPJSON_KEY]
            assert set(j.keys()) == {self.ZIPJSON_KEY}
        except AssertionError:
            if insist:
                raise RuntimeError(
                    "JSON not in the expected format {"
                    + str(self.ZIPJSON_KEY)
                    + ": zipstring}"
                )
            else:
                return j

        try:
            decoded = base64.b64decode(j[self.ZIPJSON_KEY])
            decompressed = zlib.decompress(decoded)
        except zlib.error:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            decompressed = json.loads(decompressed, cls=MyJsonDecoder)
        except TypeError and json.JSONDecodeError:
            raise RuntimeError("Could interpret the unzipped contents")

        return decompressed


class DateHandler:
    @staticmethod
    def utc_timestamp() -> float:
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    @staticmethod
    def get_timestamp_from_utc(ts: float) -> str:
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%d/%m/%y %H:%M:%S.%f")


class DataDirHandler:
    def __init__(self):
        self.BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.data_dir = self.BASE_DIR / "data"
        self.test_data_dir = self.BASE_DIR / "cursor" / "tests" / "data"

    def gcode(self, folder) -> pathlib.Path:
        return self.data_dir / "experiments" / folder / "gcode"

    def jpg(self, subfolder) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "jpg"

    def video(self, subfolder) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "video"

    def svg(self, subfolder) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "svg"

    def hpgl(self, subfolder) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "hpgl"

    def source(self, subfolder) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "source"

    def images(self) -> pathlib.Path:
        return self.data_dir / "jpg"

    def videos(self) -> pathlib.Path:
        return self.data_dir / "video"

    def gcodes(self) -> pathlib.Path:
        return self.data_dir / "gcode"

    def svgs(self) -> pathlib.Path:
        return self.data_dir / "svg"

    def hpgls(self) -> pathlib.Path:
        return self.data_dir / "hpgl"

    def ascii(self) -> pathlib.Path:
        return self.data_dir / "ascii"

    def recordings(self) -> pathlib.Path:
        return self.data_dir / "recordings"

    def test_images(self) -> pathlib.Path:
        return self.test_data_dir / "jpg"

    def test_videos(self) -> pathlib.Path:
        return self.test_data_dir / "video"

    def test_gcodes(self) -> pathlib.Path:
        return self.test_data_dir / "gcode"

    def test_svgs(self) -> pathlib.Path:
        return self.test_data_dir / "svg"

    def test_hpgls(self) -> pathlib.Path:
        return self.test_data_dir / "hpgl"

    def test_ascii(self) -> pathlib.Path:
        return self.test_data_dir / "ascii"

    def test_recordings(self) -> pathlib.Path:
        return self.test_data_dir / "test_recordings"

    def test_data_file(self, fname: str) -> pathlib.Path:
        return self.test_data_dir / fname

    def file(self, fname: str) -> pathlib.Path:
        return self.data_dir / fname
