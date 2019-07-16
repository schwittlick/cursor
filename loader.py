import os
import jsonpickle


class Loader(object):
    recordings = []
    keyboard_recordings = []

    def __init__(self, path):
        onlyfiles = [f for f in os.listdir(path) if self.is_file_and_json(os.path.join(path, f))]
        for file in onlyfiles:
            full_path = os.path.join(path, file)
            with open(full_path) as json_file:
                lines = json_file.readlines()
                data = jsonpickle.decode(lines[0])
                for line in data['mouse']:
                    self.recordings.append(line)
                for keys in data['keys']:
                    self.keyboard_recordings.append((keys[0], keys[1]))
        print('Loaded ' + str(len(self.recordings)) + ' paths from ' + str(len(onlyfiles)) + ' recording-files.')
        print('Loaded ' + str(len(self.keyboard_recordings)) + ' keys from ' + str(len(onlyfiles)) + ' recording-files.')

    @staticmethod
    def is_file_and_json(path):
        if os.path.isfile(path) and path.endswith('.json'):
            return True
        return False

    def get_all(self):
        return self.recordings

    def get(self, id):
        max_index = len(self.recordings) - 1
        if id > max_index:
            raise IndexError('Specified index too high. (> '+str(max_index)+')')
        single_recording = self.recordings[id]
        return single_recording


if __name__ == "__main__":
    path = 'data/recordings/'
    loader = Loader(path=path)
    rec = loader.get(0)
    print(rec)

    all = loader.get_all()
    print(all)