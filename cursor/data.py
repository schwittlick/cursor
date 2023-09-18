import pathlib
import datetime
import pytz


class DateHandler:
    @staticmethod
    def utc_timestamp() -> float:
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    @staticmethod
    def datetime_from_timestamp(ts: float):
        return datetime.datetime.fromtimestamp(ts)

    @staticmethod
    def get_timestamp_from_utc(ts: float) -> str:
        dt = DateHandler.datetime_from_timestamp(ts)
        return dt.strftime("%d/%m/%y %H:%M:%S.%f")


class DataDirHandler:
    def __init__(self):
        self.BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
        self.data_dir = self.BASE_DIR / "data"
        self.test_data_dir = self.BASE_DIR / "cursor" / "tests" / "data"

    def gcode(self, folder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / folder / "gcode"

    def tek(self, folder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / folder / "tek"

    def digi(self, folder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / folder / "digi"

    def jpg(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "jpg"

    def video(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "video"

    def svg(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "svg"

    def hpgl(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "hpgl"

    def pickle(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "pickle"

    def source(self, subfolder: str) -> pathlib.Path:
        return self.data_dir / "experiments" / subfolder / "source"

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

    def test_ascii(self) -> pathlib.Path:
        return self.test_data_dir / "ascii"

    def test_recordings(self) -> pathlib.Path:
        return self.test_data_dir / "test_recordings"

    def test_data_file(self, fname: str) -> pathlib.Path:
        return self.test_data_dir / fname

    def file(self, fname: str) -> pathlib.Path:
        return self.data_dir / fname

    def pickles(self) -> pathlib.Path:
        return self.data_dir / "pickles"
