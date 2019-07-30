from ..cursor import path

import os
import json


class Loader:
    def __init__(self, directory):
        self._recordings = []
        self._keyboard_recordings = []

        all_json_files = [f for f in os.listdir(directory) if self.is_file_and_json(os.path.join(directory, f))]
        for file in all_json_files:
            full_path = os.path.join(directory, file)
            print(full_path)
            with open(full_path) as json_file:
                json_string = json_file.readline()
                data = json.loads(json_string, cls=path.MyJsonDecoder)
                self._recordings.append(data['mouse'])
                for keys in data['keys']:
                    self._keyboard_recordings.append((keys[0], keys[1]))
        print('Loaded ' + str(len(self._recordings)) + ' paths from ' + str(len(all_json_files)) + ' recording-files.')
        print('Loaded ' + str(len(self._keyboard_recordings)) + ' keys from ' + str(len(all_json_files)) + ' recording-files.')

    @staticmethod
    def is_file_and_json(path):
        if os.path.isfile(path) and path.endswith('.json'):
            return True
        return False

    def all(self):
        """
        :return: a copy of all recordings
        """
        return list(self._recordings)

    def single(self, index):
        max_index = len(self._recordings) - 1
        if index > max_index:
            raise IndexError('Specified index too high. (> '+str(max_index)+')')
        single_recording = self._recordings[index]
        return single_recording

    def keys(self):
        return self._keyboard_recordings