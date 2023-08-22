from __future__ import annotations

import pathlib

import wasabi

from cursor.collection import Collection
from cursor.renderer.jpg import JpegRenderer

log = wasabi.Printer()


class AsciiRenderer:
    def __init__(self, folder: pathlib.Path, jpeg_renderer: JpegRenderer):
        self.save_path = folder
        self.jpeg_renderer = jpeg_renderer
        self.pixels = " .,:;i1tfLCG08#"
        self.output = ""

    def get_raw_char(self, r: int, g: int, b: int, a: int) -> str:
        value = r  # self.intensity(r, g, b, a)
        precision = 255 / (len(self.pixels) - 1)
        rawChar = self.pixels[int(round(value / precision))]

        return rawChar

    @staticmethod
    def intensity(r: int, g: int, b: int, a: int) -> int:
        return (r + g + b) * a

    def render(
            self,
            paths: Collection,
            scale: float = 1.0,
            frame: bool = False,
            thickness: int = 1,
    ):
        self.jpeg_renderer.render(paths, scale, frame, thickness)

        im = self.jpeg_renderer.img

        columns = 100
        rows = 50

        im = im.resize((columns, rows))
        px = im.load()
        size = im.size
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                _px = px[x, y]
                _a = self.get_raw_char(_px[0], _px[1], _px[2], 1)
                self.output = self.output + _a
            self.output = self.output + "\n"

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
        fname = self.save_path / (filename + ".txt")
        with open(fname.as_posix(), "w") as file:
            file.write(self.output)
        log.good(f"Finished saving {fname}")
