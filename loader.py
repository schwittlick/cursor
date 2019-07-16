import os
import jsonpickle


class Loader(object):
    recordings = []
    keyboard_recordings = []

    def __init__(self, path):
        all_json_files = [f for f in os.listdir(path) if self.is_file_and_json(os.path.join(path, f))]
        for file in all_json_files:
            full_path = os.path.join(path, file)
            with open(full_path) as json_file:
                json_string = json_file.readline()
                data = jsonpickle.decode(json_string)
                resolution = data['resolution']
                for line in data['mouse']:
                    self.recordings.append(line)
                for keys in data['keys']:
                    self.keyboard_recordings.append((keys[0], keys[1]))
        print('Loaded ' + str(len(self.recordings)) + ' paths from ' + str(len(all_json_files)) + ' recording-files.')
        print('Loaded ' + str(len(self.keyboard_recordings)) + ' keys from ' + str(len(all_json_files)) + ' recording-files.')

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