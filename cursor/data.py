import pathlib


class DataHandler:
    def __init__(self):
        self.BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.data_dir = self.BASE_DIR.joinpath("data")
        self.test_data_dir = self.BASE_DIR.joinpath("tests").joinpath("data")

    def gcode(self, folder):
        return self.data_dir.joinpath("experiments").joinpath(folder).joinpath("gcode")

    def jpg(self, subfolder):
        return self.data_dir.joinpath("experiments").joinpath(subfolder).joinpath("jpg")

    def svg(self, subfolder):
        return self.data_dir.joinpath("experiments").joinpath(subfolder).joinpath("svg")

    def images(self):
        return self.data_dir.joinpath("jpgs")

    def gcodes(self):
        return self.data_dir.joinpath("gcode")

    def svgs(self):
        return self.data_dir.joinpath("svg")

    def recordings(self):
        return self.data_dir.joinpath("recordings")

    def test_images(self):
        return self.test_data_dir.joinpath("jpgs")

    def test_gcodes(self):
        return self.test_data_dir.joinpath("gcode")

    def test_svgs(self):
        return self.test_data_dir.joinpath("svg")

    def test_recordings(self):
        return self.test_data_dir.joinpath("test_recordings")
