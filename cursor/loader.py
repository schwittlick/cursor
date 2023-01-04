from cursor.data import DateHandler
from cursor.path import Path
from cursor.position import Position
from cursor.collection import Collection
from cursor.misc import Timer

import wasabi
import typing
import pathlib
import json
import base64
import zlib
import pyautogui
from functools import reduce

log = wasabi.Printer()


class MyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Collection):
            return {
                "paths": o.get_all(),
                "timestamp": o.timestamp(),
            }

        if isinstance(o, Path):
            return o.vertices

        if isinstance(o, Position):
            return {
                "x": round(o.x, 4),
                "y": round(o.y, 4),
                "ts": round(o.timestamp, 2),
                "c": o.color if o.color else None,
            }


class MyJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    # @profile
    def object_hook(self, dct):
        if "x" in dct:
            if "c" in dct:
                if dct["c"] is not None:
                    c = tuple(dct["c"])
                else:
                    c = None
            else:
                c = None
            return Position(dct["x"], dct["y"], dct["ts"], c)
        if "w" in dct and "h" in dct:
            s = pyautogui.Size(dct["w"], dct["h"])
            return s
        if "paths" in dct and "timestamp" in dct:
            ts = dct["timestamp"]
            pc = Collection(ts)
            for _p in dct["paths"]:
                pc.add(Path(_p))
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

    # @profile
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



class HPGLLoader:
    def __init__(self, fn: pathlib.Path):
        from misc import parse_hpgl

        # why parse hpgl
        pathlist = parse_hpgl(fn.as_posix())

class Loader:
    def __init__(
        self,
        directory: pathlib.Path = None,
        limit_files: typing.Union[int, list[str]] = None,
        load_keys: bool = False,
    ):
        self._recordings = []
        self._keyboard_recordings = []

        if directory is not None:
            self.load_all(
                directory=directory, limit_files=limit_files, load_keys=load_keys
            )

    def load_all(
        self,
        directory: pathlib.Path,
        limit_files: typing.Union[int, list[str]] = None,
        load_keys: bool = False,
    ) -> None:
        t = Timer()
        t.start()
        all_json_files = [
            f for f in directory.iterdir() if self.is_file_and_json(directory / f)
        ]

        fin = []
        if limit_files and type(limit_files) is int:
            all_json_files = all_json_files[:limit_files]
        if limit_files and type(limit_files) is list:
            for f in all_json_files:
                st = f.stem
                if st in limit_files:
                    fin.append(f)
            # all_json_files = [k for k in all_json_files if k.stem in limit_files]
            all_json_files = fin

        for file in all_json_files:
            full_path = directory / file
            self.load_file(full_path, load_keys)

        absolut_path_count = sum(len(pc) for pc in self._recordings)

        for pc in self._recordings:
            # pc.limit()
            pc.clean()

        log.info(
            f"Loaded {absolut_path_count} paths from {len(self._recordings)} recordings"
        )
        log.info(
            f"Loaded {len(self._keyboard_recordings)} keys from {len(all_json_files)} recordings"
        )
        log.info(f"This took {round(t.elapsed() * 1000)}ms.")

    def load_file(self, path: pathlib.Path, load_keys: bool = False) -> None:
        assert "_" in path.stem
        # everything before _ will be interpreted as a timestamp
        idx = path.stem.index("_")
        _fn = path.stem[:idx]
        ts = DateHandler.get_timestamp_from_utc(float(_fn))
        log.info(f"Loading {path.stem}.json > {ts}")

        new_keys = []
        with open(path.as_posix()) as json_file:
            json_string = json_file.readline()
            try:
                jd = eval(json_string)
                _data = JsonCompressor().json_unzip(jd)
            except RuntimeError:
                _data = json.loads(json_string, cls=MyJsonDecoder)
            self._recordings.append(_data["mouse"])
            if load_keys:
                for keys in _data["keys"]:
                    new_keys.append(tuple(keys))

        self._keyboard_recordings.extend(new_keys)
        log.good(f"Loaded {len(self._recordings[-1])} paths")
        log.good(f"Loaded {len(new_keys)} keys")

    @staticmethod
    def is_file_and_json(path: pathlib.Path) -> bool:
        if path.is_file() and path.as_posix().endswith(".json"):
            return True
        return False

    def all_collections(self) -> list[Collection]:
        """
        :return: a copy of all recordings
        """
        return list(self._recordings)

    def all_paths(self) -> Collection:
        """
        :return: all paths combined into one collection.PathCollection
        """
        return reduce(lambda pcol1, pcol2: pcol1 + pcol2, self._recordings)

    def single(self, index: int) -> Path:
        max_index = len(self._recordings) - 1
        if index > max_index:
            raise IndexError("Specified index too high. (> " + str(max_index) + ")")
        single_recording = self._recordings[index]
        return single_recording

    def keys(self) -> list[tuple]:
        return self._keyboard_recordings

    def __len__(self) -> int:
        return len(self._recordings)
