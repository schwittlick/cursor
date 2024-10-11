import configparser
import pathlib
from typing import Optional
import os
import logging


def load_cursor_config(config_path: str = "config.ini") -> str:
    config: configparser.ConfigParser = configparser.ConfigParser()

    # Try to read the config file, if it exists
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        # Use default values if the config file doesn't exist
        logging.warning(
            f"Config file '{config_path}' not found. Using default values.")
        config['cursor'] = {
            'data_dir': '/tmp/cursor_data',
            'log_level': 'INFO'
        }

    if "cursor" not in config:
        raise ValueError(
            "The 'cursor' section is missing from the config file.")

    data_dir: Optional[str] = config["cursor"].get("data_dir")
    log_level: Optional[str] = config["cursor"].get("log_level")

    if log_level:
        log_level = log_level.upper()
        numeric_level: int = getattr(logging, log_level, logging.INFO)
        logging.basicConfig(
            level=numeric_level, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    if data_dir and not os.path.isdir(data_dir):
        logging.warning(f"The specified data_dir '{data_dir}' does not exist.")

    return data_dir


class DataDirHandler:
    def __init__(self):
        base_dir = pathlib.Path(__file__).resolve().parent.parent
        ini_path = base_dir / "config_local.ini"
        data_dir_cfg = load_cursor_config(ini_path.as_posix())

        self.data_dir = pathlib.Path(data_dir_cfg)

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

    def file(self, fname: str) -> pathlib.Path:
        return self.data_dir / fname
