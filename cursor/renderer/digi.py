from __future__ import annotations

import pathlib

import wasabi

from cursor.collection import Collection

log = wasabi.Printer()


class DigiplotRenderer:
    def __init__(
            self,
            folder: pathlib.Path,
    ):
        self.__save_path = folder
        self.__paths = Collection()

        self.PEN_DOWN = "I;"
        self.PEN_UP = "H;"
        self.GO_ABSOLUTE = "K;"

    def render(self, paths: Collection) -> None:
        self.__paths += paths
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")

    @staticmethod
    def _coord_string(x: int, y: int) -> str:
        return f"X,{x};/Y,{y};"  # coord + go absolute

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".digi")

        output_string = ""

        for p in self.__paths:
            x = int(p.start_pos().x)
            y = int(p.start_pos().y)
            output_string += self._coord_string(x, y)
            output_string += self.PEN_UP
            output_string += self.GO_ABSOLUTE
            for line in p.generate:
                x = int(line.x)
                y = int(line.y)
                output_string += self._coord_string(x, y)
                output_string += self.PEN_DOWN
                output_string += self.GO_ABSOLUTE

        output_string += self._coord_string(0, 0)
        output_string += self.PEN_UP
        output_string += self.GO_ABSOLUTE

        with open(fname.as_posix(), "wb") as file:
            file.write(output_string.encode("utf-8"))

        log.good(f"Finished saving {fname}")

        return output_string
