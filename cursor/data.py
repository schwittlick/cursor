import pathlib


class DataDirHandler:
    def __init__(self):
        self.BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.data_dir = self.BASE_DIR / "data"
        self.test_data_dir = self.BASE_DIR / "cursor" / "tests" / "data"

    def __create(self, folder: pathlib.Path) -> pathlib.Path:
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def __sub(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder

    def gcode(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "gcode")

    def tek(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "tek")

    def digi(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "digi")

    def jpg(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "jpg")

    def video(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "video")

    def svg(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "svg")

    def hpgl(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "hpgl")

    def pickle(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "pickle")

    def pdf(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "pdf")

    def source(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "source")

    def images(self) -> pathlib.Path:
        return self.data_dir / "jpg"

    def videos(self) -> pathlib.Path:
        return self.data_dir / "video"

    def gcodes(self) -> pathlib.Path:
        return self.data_dir / "gcode"

    def svgs(self) -> pathlib.Path:
        return self.data_dir / "svg"

    def hpgls(self) -> pathlib.Path:
        return self.data_dir / "hpgl"

    def pickles(self) -> pathlib.Path:
        return self.data_dir / "pickle"

    def pdfs(self) -> pathlib.Path:
        return self.data_dir / "pdf"

    def ascii(self) -> pathlib.Path:
        return self.data_dir / "ascii"

    def recordings(self) -> pathlib.Path:
        return self.data_dir / "recordings"

    def recordings_legacy(self) -> pathlib.Path:
        return self.data_dir / "recordings_legacy"

    def recordings_simplified(self) -> pathlib.Path:
        return self.data_dir / "recordings_simplified"

    def recordings_legacy_simplified(self) -> pathlib.Path:
        return self.data_dir / "recordings_legacy_simplified"

    def recordings_all(self) -> pathlib.Path:
        return self.data_dir / "recordings_all"

    def test_images(self) -> pathlib.Path:
        return self.test_data_dir / "jpg"

    def test_videos(self) -> pathlib.Path:
        return self.test_data_dir / "video"

    def test_gcodes(self) -> pathlib.Path:
        return self.test_data_dir / "gcode"

    def test_svgs(self) -> pathlib.Path:
        return self.test_data_dir / "svg"

    def test_hpgls(self) -> pathlib.Path:
        return self.test_data_dir / "hpgl"

    def test_pickles(self) -> pathlib.Path:
        return self.test_data_dir / "pickle"

    def test_pdfs(self) -> pathlib.Path:
        return self.test_data_dir / "pdf"

    def test_ascii(self) -> pathlib.Path:
        return self.test_data_dir / "ascii"

    def test_recordings(self) -> pathlib.Path:
        return self.test_data_dir / "test_recordings"

    def test_data_file(self, fname: str) -> pathlib.Path:
        return self.test_data_dir / fname

    def file(self, fname: str) -> pathlib.Path:
        return self.data_dir / fname
