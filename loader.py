import os
import json


class CursorLoader(object):
    recordings = []

    def __init__(self, path):
        onlyfiles = [f for f in os.listdir(path) if self.file_and_json(os.path.join(path, f))]
        for file in onlyfiles:
            full_path = os.path.join(path, file)
            with open(full_path) as json_file:
                data = json.load(json_file)
                for line in data:
                    current_line = []
                    for point in line:
                        current_line.append((point[0], point[1], point[2]))
                    self.recordings.append(current_line)

    def file_and_json(self, path):
        if os.path.isfile(path) and path.endswith('.json'):
            return True
        return False


if __name__ == "__main__":
    path = 'data/recordings/'
    loader = CursorLoader(path=path)