from cursor import path

import os
import json
import time


class Loader:
    def __init__(self, directory, limit_files=None):
        start_benchmark = time.time()

        self._recordings = []
        self._keyboard_recordings = []

        all_json_files = [
            f
            for f in os.listdir(directory)
            if self.is_file_and_json(os.path.join(directory, f))
        ]

        if limit_files:
            all_json_files = all_json_files[:limit_files]

        for file in all_json_files:
            full_path = os.path.join(directory, file)
            print(full_path)
            with open(full_path) as json_file:
                json_string = json_file.readline()
                try:
                    jd = eval(json_string)
                    data = path.JsonCompressor().json_unzip(jd)
                except RuntimeError:
                    data = json.loads(json_string, cls=path.MyJsonDecoder)
                self._recordings.append(data["mouse"])
                for keys in data["keys"]:
                    self._keyboard_recordings.append((keys[0], keys[1]))

        absolut_path_count = sum(len(pc) for pc in self._recordings)

        for pc in self._recordings:
            pc.clean()

        elapsed = time.time() - start_benchmark
        print(
            f"Loaded {absolut_path_count} paths from {len(self._recordings)} recordings."
        )
        print(
            f"Loaded {len(self._keyboard_recordings)} keys from {len(all_json_files)} recordings."
        )
        print(f"This took {round(elapsed * 1000)}ms.")

    @staticmethod
    def is_file_and_json(path):
        if os.path.isfile(path) and path.endswith(".json"):
            return True
        return False

    def all_collections(self):
        """
        :return: a copy of all recordings
        """
        return list(self._recordings)

    def all_paths(self):
        from functools import reduce

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
