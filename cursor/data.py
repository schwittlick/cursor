import os

class DataHandler:
    @staticmethod
    def recordings():
        return os.path.abspath('../data/recordings/')

    @staticmethod
    def test_recordings():
        return os.path.abspath('../tests/data/recordings/')