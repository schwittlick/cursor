import os

class DataHandler:
    @staticmethod
    def data_path():
        return os.path.abspath('../data/recordings/')

    @staticmethod
    def test_data_path():
        return os.path.abspath('../tests/data/recordings/')