from __future__ import annotations

import ast
import json
import logging
import os
import pathlib
import signal
import time
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from functools import reduce

from tqdm import tqdm

from cursor.collection import Collection
from cursor.load import KeyPress
from cursor.load.compress import JsonCompressor
from cursor.load.decode import MyJsonDecoder
from cursor.path import Path
from cursor.timer import Timer, DateHandler


def _load_file_worker(
    path: pathlib.Path, load_keys: bool, verbose: bool
) -> tuple[Collection, list[KeyPress]]:
    """Module-level worker for ProcessPoolExecutor.

    Must be a module-level function (not a bound method) so it can be pickled
    by the process pool. Each worker process runs in its own GIL, so multiple
    files are decoded in true parallel.
    """
    assert "_" in path.stem

    if verbose:
        logging.info(f"Loading {path.stem}.json")

    t0 = time.perf_counter()
    json_string = path.read_text()
    t1 = time.perf_counter()
    try:
        jd = ast.literal_eval(json_string)
        t2 = time.perf_counter()
        _data = JsonCompressor().json_unzip(jd)
    except RuntimeError:
        t2 = time.perf_counter()
        _data = json.loads(json_string, cls=MyJsonDecoder)
    t3 = time.perf_counter()

    if verbose:
        logging.info(
            f"  read={int((t1 - t0) * 1000)}ms "
            f"eval={int((t2 - t1) * 1000)}ms "
            f"total={int((t3 - t0) * 1000)}ms"
        )

    collection = _data["mouse"]
    new_keys: list[KeyPress] = []
    if load_keys:
        for key in _data["keys"]:
            is_down = bool(key[2]) if len(key) > 2 else True
            new_keys.append(KeyPress(key[0], key[1], is_down))

    return collection, new_keys


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
            self.load_all(directory=directory, limit_files=limit_files, load_keys=load_keys)

    def load_all(
        self,
        directory: pathlib.Path,
        limit_files: int | list[str] | None = None,
        load_keys: bool = False,
    ) -> None:
        t = Timer()
        t.start()
        all_json_files = [f for f in directory.glob("*.json") if f.is_file()]

        if limit_files and type(limit_files) is int:
            all_json_files = all_json_files[:limit_files]
        elif limit_files and type(limit_files) is list:
            all_json_files = [f for f in all_json_files if f.stem in limit_files]

        logging.info(f"Loading {len(all_json_files)} recording files...")
        # Workers ignore SIGINT so only the main process handles Ctrl+C.
        # On interrupt we cancel pending futures and wait for the few
        # already-running ones to finish naturally — no atexit cleanup mess.
        executor = ProcessPoolExecutor(
            initializer=signal.signal,
            initargs=(signal.SIGINT, signal.SIG_IGN),
        )
        # Throttled submission: keep at most max_in_flight futures queued at
        # once so decoded-but-unconsumed Collection objects don't pile up in
        # memory while slower files are still being processed.
        max_in_flight = (os.cpu_count() or 4) * 2
        file_iter = iter(all_json_files)
        pending: set = set()

        def _submit_next():
            f = next(file_iter, None)
            if f is not None:
                pending.add(executor.submit(_load_file_worker, f, load_keys, self.verbose))

        try:
            with tqdm(total=len(all_json_files)) as pbar:
                for _ in range(max_in_flight):
                    _submit_next()
                while pending:
                    done, _ = wait(pending, return_when=FIRST_COMPLETED)
                    for future in done:
                        pending.discard(future)
                        collection, keys = future.result()
                        collection.clean()
                        self._recordings.append(collection)
                        self._keyboard_recordings.extend(keys)
                        pbar.update(1)
                        _submit_next()
        except KeyboardInterrupt:
            executor.shutdown(wait=True, cancel_futures=True)
            logging.warning("Loading interrupted.")
            raise
        else:
            executor.shutdown(wait=False)

        absolut_path_count = sum(len(pc) for pc in self._recordings)
        logging.info(f"Loaded {absolut_path_count} paths from {len(self._recordings)} recordings")
        logging.info(f"Loaded {len(self._keyboard_recordings)} keys from {len(all_json_files)} recordings")
        logging.info(f"This took {round(t.elapsed() * 1000)}ms.")

    def _load_file_result(self, path: pathlib.Path, load_keys: bool = False) -> tuple[Collection, list[KeyPress]]:
        return _load_file_worker(path, load_keys, self.verbose)

    def load_file(self, path: pathlib.Path, load_keys: bool = False) -> None:
        collection, keys = self._load_file_result(path, load_keys)
        self._recordings.append(collection)
        self._keyboard_recordings.extend(keys)

    @staticmethod
    def is_file_and_json(path: pathlib.Path) -> bool:
        return path.is_file() and path.suffix == ".json"

    def all_collections(self) -> list[Collection]:
        return list(self._recordings)

    def all_paths(self) -> Collection:
        return reduce(lambda pcol1, pcol2: pcol1 + pcol2, self._recordings)

    def single(self, index: int) -> Path:
        if index > len(self._recordings) - 1:
            raise IndexError("Specified index too high. (> " + str(len(self._recordings) - 1) + ")")
        return self._recordings[index]

    def keys(self) -> list[KeyPress]:
        return self._keyboard_recordings

    def __len__(self) -> int:
        return len(self._recordings)
