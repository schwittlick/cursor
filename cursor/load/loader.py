from __future__ import annotations

import json
import logging
import pathlib
from functools import reduce

from tqdm import tqdm

from cursor.collection import Collection
from cursor.load import KeyPress
from cursor.load.compress import JsonCompressor
from cursor.load.decode import MyJsonDecoder
from cursor.path import Path
from cursor.timer import Timer, DateHandler


class Loader:
    def __init__(
            self,
            directory: pathlib.Path = None,
            limit_files: int | list[str] | None = None,
            load_keys: bool = False,
    ):
        self.verbose = True

        self._recordings = []
        self._keyboard_recordings: list[KeyPress] = []

        if directory is not None:
            self.load_all(
                directory=directory, limit_files=limit_files, load_keys=load_keys
            )

    def load_all(
            self,
            directory: pathlib.Path,
            limit_files: int | list[str] | None = None,
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

        logging.info(f"Loading {len(all_json_files)} recording files...")
        with tqdm(total=len(all_json_files)) as pbar:
            pbar.update(0)
            for file in all_json_files:
                full_path = directory / file
                self.load_file(full_path, load_keys)
                pbar.update(1)

        absolut_path_count = sum(len(pc) for pc in self._recordings)

        for pc in self._recordings:
            # pc.limit()
            pc.clean()

        logging.info(
            f"Loaded {absolut_path_count} paths from {len(self._recordings)} recordings"
        )
        logging.info(
            f"Loaded {len(self._keyboard_recordings)} keys from {len(all_json_files)} recordings"
        )
        logging.info(f"This took {round(t.elapsed() * 1000)}ms.")

    def load_file(self, path: pathlib.Path, load_keys: bool = False) -> None:
        assert "_" in path.stem
        # everything before _ will be interpreted as a timestamp
        idx = path.stem.index("_")
        _fn = path.stem[:idx]
        ts = DateHandler.get_timestamp_from_utc(float(_fn))

        if self.verbose:
            logging.info(f"Loading {path.stem}.json > {ts}")

        new_keys: list[KeyPress] = []
        with open(path.as_posix()) as json_file:
            json_string = json_file.readline()
            try:
                jd = eval(json_string)
                _data = JsonCompressor().json_unzip(jd)
            except RuntimeError:
                _data = json.loads(json_string, cls=MyJsonDecoder)
            self._recordings.append(_data["mouse"])
            if load_keys:
                for key in _data["keys"]:
                    char = key[0]
                    timestamp = key[1]

                    # some legacy recordings dont have information if its key-up or key-down
                    is_down = key[2] if len(key) > 2 else 1
                    new_keys.append(KeyPress(char, timestamp, is_down))

        self._keyboard_recordings.extend(new_keys)
        if self.verbose:
            logging.info(f"Loaded {len(self._recordings[-1])} paths")
            logging.info(f"Loaded {len(new_keys)} keys")

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

    def keys(self) -> list[KeyPress]:
        return self._keyboard_recordings

    def __len__(self) -> int:
        return len(self._recordings)
