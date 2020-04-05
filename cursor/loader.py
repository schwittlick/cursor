from cursor import data

import json
import time
import wasabi
import pathlib
from functools import reduce

log = wasabi.Printer()


class Loader:
    def __init__(self, directory, limit_files=None):
        assert isinstance(directory, pathlib.Path), "Only path objects allowed"
        start_benchmark = time.time()

        self._recordings = []
        self._keyboard_recordings = []

        all_json_files = [
            f
            for f in directory.iterdir()
            if self.is_file_and_json(directory.joinpath(f))
        ]

        if limit_files:
            all_json_files = all_json_files[:limit_files]

        for file in all_json_files:
            full_path = directory.joinpath(file)
            log.good(f"Loading {full_path}")
            with open(full_path.as_posix()) as json_file:
                json_string = json_file.readline()
                try:
                    jd = eval(json_string)
                    _data = data.JsonCompressor().json_unzip(jd)
                except RuntimeError:
                    _data = json.loads(json_string, cls=data.MyJsonDecoder)
                self._recordings.append(_data["mouse"])
                for keys in _data["keys"]:
                    self._keyboard_recordings.append((keys[0], keys[1]))

        absolut_path_count = sum(len(pc) for pc in self._recordings)

        for pc in self._recordings:
            pc.clean()

        elapsed = time.time() - start_benchmark
        log.good(
            f"Loaded {absolut_path_count} paths from {len(self._recordings)} recordings."
        )
        log.good(
            f"Loaded {len(self._keyboard_recordings)} keys from {len(all_json_files)} recordings."
        )
        log.good(f"This took {round(elapsed * 1000)}ms.")

    @staticmethod
    def is_file_and_json(path):
        assert isinstance(path, pathlib.Path), "Only path objects allowed"
        if path.is_file() and path.as_posix().endswith(".json"):
            return True
        return False

    def all_collections(self):
        """
        :return: a copy of all recordings
        """
        return list(self._recordings)

    def all_paths(self):
        return reduce(lambda pcol1, pcol2: pcol1 + pcol2, self._recordings)

    def single(self, index):
        max_index = len(self._recordings) - 1
        if index > max_index:
            raise IndexError("Specified index too high. (> " + str(max_index) + ")")
        single_recording = self._recordings[index]
        return single_recording

    def keys(self):
        return self._keyboard_recordings

    def __len__(self):
        return len(self._recordings)
