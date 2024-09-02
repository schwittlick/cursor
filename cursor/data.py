import configparser
import pathlib
from typing import Dict, Optional
import os
import logging


def load_cursor_config(config_path: str = 'config.ini') -> Dict[str, Optional[str]]:
    # Create a ConfigParser object
    config: configparser.ConfigParser = configparser.ConfigParser()

    # Read the configuration file
    config.read(config_path)

    # Check if the 'cursor' section exists
    if 'cursor' not in config:
        raise ValueError("The 'cursor' section is missing from the config file.")

    # Get the values from the 'cursor' section
    data_dir: Optional[str] = config['cursor'].get('data_dir')
    log_level: Optional[str] = config['cursor'].get('log_level')

    # Convert log_level to uppercase if it exists
    if log_level:
        log_level = log_level.upper()

    # Set up logging
    numeric_level: int = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')

    # Validate data_dir
    if data_dir and not os.path.isdir(data_dir):
        logging.warning(f"The specified data_dir '{data_dir}' does not exist.")

    return {
        'data_dir': data_dir,
        'log_level': log_level
    }


class DataDirHandler:
    def __init__(self):
        base_dir = pathlib.Path(__file__).resolve().parent.parent
        ini_path = base_dir / "config_local.ini"
        cursor_config: Dict[str, Optional[str]] = load_cursor_config(ini_path.as_posix())

        self.data_dir = pathlib.Path(cursor_config['data_dir'])
        self.test_data_dir = base_dir / "cursor" / "tests" / "data"

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

    def png(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "png")

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

    def json(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "json")

    def source(self, subfolder: str) -> pathlib.Path:
        return self.__create(self.__sub(subfolder) / "source")

    def jpgs(self) -> pathlib.Path:
        return self.data_dir / "jpg"

    def pngs(self) -> pathlib.Path:
        return self.data_dir / "pngs"

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

    def jsons(self) -> pathlib.Path:
        return self.data_dir / "json"

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
