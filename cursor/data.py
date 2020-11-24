import pathlib
import json
import base64
import zlib
import pyautogui
import datetime
import pytz


class MyJsonEncoder(json.JSONEncoder):

    def default(self, o):
        from cursor.path import Path
        from cursor.path import PathCollection
        from cursor.path import TimedPosition

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

        j = {
            self.ZIPJSON_KEY: base64.b64encode(
                zlib.compress(json.dumps(j, cls=MyJsonEncoder).encode("utf-8"))
            ).decode("ascii")
        }

        return j

    def json_unzip(self, j, insist=True):
        try:
            assert j[self.ZIPJSON_KEY]
            assert set(j.keys()) == {self.ZIPJSON_KEY}
        except:
            if insist:
                raise RuntimeError(
                    "JSON not in the expected format {"
                    + str(self.ZIPJSON_KEY)
                    + ": zipstring}"
                )
            else:
                return j

        try:
            j = zlib.decompress(base64.b64decode(j[self.ZIPJSON_KEY]))
        except:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            j = json.loads(j, cls=MyJsonDecoder)
        except:
            raise RuntimeError("Could interpret the unzipped contents")

        return j


class DateHandler:
    @staticmethod
    def utc_timestamp():
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    @staticmethod
    def get_timestamp_from_utc(ts):
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%d/%m/%y %H:%M:%S.%f")


class DataDirHandler:
    def __init__(self):
        self.BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.data_dir = self.BASE_DIR.joinpath("data")
        self.test_data_dir = (
            self.BASE_DIR.joinpath("cursor").joinpath("tests").joinpath("data")
        )

    def gcode(self, folder):
        return self.data_dir.joinpath("experiments").joinpath(folder).joinpath("gcode")

    def jpg(self, subfolder):
        return self.data_dir.joinpath("experiments").joinpath(subfolder).joinpath("jpg")

    def svg(self, subfolder):
        return self.data_dir.joinpath("experiments").joinpath(subfolder).joinpath("svg")

    def hpgl(self, subfolder):
        return (
            self.data_dir.joinpath("experiments").joinpath(subfolder).joinpath("hpgl")
        )

    def images(self):
        return self.data_dir.joinpath("jpgs")

    def gcodes(self):
        return self.data_dir.joinpath("gcode")

    def svgs(self):
        return self.data_dir.joinpath("svg")

    def hpgls(self):
        return self.data_dir.joinpath("hpgl")

    def recordings(self):
        return self.data_dir.joinpath("recordings")

    def test_images(self):
        return self.test_data_dir.joinpath("jpgs")

    def test_gcodes(self):
        return self.test_data_dir.joinpath("gcode")

    def test_svgs(self):
        return self.test_data_dir.joinpath("svg")

    def test_hpgls(self):
        return self.test_data_dir.joinpath("hpgl")

    def test_recordings(self):
        return self.test_data_dir.joinpath("test_recordings")
