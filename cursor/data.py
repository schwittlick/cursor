import os


class DataHandler:
    @staticmethod
    def images():
        return os.path.abspath('data/jpgs/')

    @staticmethod
    def gcodes():
        return os.path.abspath('data/gcode/')

    @staticmethod
    def svgs():
        return os.path.abspath('data/svg/')

    @staticmethod
    def recordings():
        return os.path.abspath('data/recordings/')

    @staticmethod
    def test_images():
        return os.path.abspath('tests/data/jpgs/')

    @staticmethod
    def test_gcodes():
        return os.path.abspath('tests/data/gcode/')

    @staticmethod
    def test_svgs():
        return os.path.abspath('tests/data/svg/')

    @staticmethod
    def test_recordings():
        return os.path.abspath('tests/data/test_recordings/')

