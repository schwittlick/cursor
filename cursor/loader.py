try:
    from ..cursor import path
except:
    try:
        import path
    except:
        from cursor import path

import os
import json
import time
import itertools


class Loader:
    def __init__(self, directory):
        start_benchmark = time.time()

        self._recordings = []
        self._keyboard_recordings = []

        all_json_files = [f for f in os.listdir(directory) if self.is_file_and_json(os.path.join(directory, f))]
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
                self._recordings.append(data['mouse'])
                for keys in data['keys']:
                    self._keyboard_recordings.append((keys[0], keys[1]))

        absolut_path_count = sum(len(pc) for pc in self._recordings)

        elapsed = time.time() - start_benchmark
        print(F"Loaded {absolut_path_count} paths from {len(self._recordings)} recordings.")
        print(F"Loaded {len(self._keyboard_recordings)} keys from {len(all_json_files)} recordings.")
        print(F"This took {round(elapsed * 1000)}ms.")

    @staticmethod
    def is_file_and_json(path):
        if os.path.isfile(path) and path.endswith('.json'):
            return True
        return False

    def all_collections(self):
        """
        :return: a copy of all recordings
        """
        return list(self._recordings)

    def all_paths(self):
        paths = []
        for coll in self._recordings:
            paths.extend(coll.get_all())
        return paths

    def single(self, index):
        max_index = len(self._recordings) - 1
        if index > max_index:
            raise IndexError('Specified index too high. (> '+str(max_index)+')')
        single_recording = self._recordings[index]
        return single_recording

    def keys(self):
        return self._keyboard_recordings