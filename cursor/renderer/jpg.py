from __future__ import annotations

import pathlib

import wasabi
from PIL import Image, ImageDraw

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.renderer import PathIterator

log = wasabi.Printer()


class JpegRenderer:
    def __init__(self, folder: pathlib.Path, w: int = 1920, h: int = 1080):
        self.save_path = folder
        self.img = None
        self.img_draw = None

        self.image_width = w
        self.image_height = h

    def render(
            self,
            paths: Collection,
            scale: float = 1.0,
            frame: bool = False,
            thickness: int = 1,
    ) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        log.good(f"Creating image with size=({self.image_width}, {self.image_height})")
        assert self.image_width < 21000 and self.image_height < 21000, "keep resolution lower"

        self.img = Image.new("RGB", (self.image_width, self.image_height), "white")
        self.img_draw = ImageDraw.ImageDraw(self.img)

        it = PathIterator(paths)

        for conn in it.connections():
            start = conn[0]
            end = conn[1]

            self.img_draw.line(
                xy=(
                    start.x * scale, self.image_height - start.y * scale, end.x * scale,
                    self.image_height - end.y * scale),
                fill="black",
                width=thickness,
            )

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        fname = self.save_path / (filename + ".jpg")
        self.img.save(fname, "JPEG")
        log.good(f"Finished saving {fname}")

    def image(self) -> Image:
        return self.img

    def render_bb(self, bb: BoundingBox) -> None:
        self.img_draw.line(xy=(bb.x, bb.y, bb.x2, bb.y), fill="black", width=2)
        self.img_draw.line(xy=(bb.x, bb.y, bb.x, bb.y2), fill="black", width=2)
        self.img_draw.line(xy=(bb.x2, bb.y, bb.x2, bb.y2), fill="black", width=2)
        self.img_draw.line(xy=(bb.x, bb.y2, bb.x2, bb.y2), fill="black", width=2)

    def render_frame(self) -> None:
        w = self.img.size[0]
        h = self.img.size[1]
        self.img_draw.line(xy=(0, 0, w, 0), fill="black", width=2)
        self.img_draw.line(xy=(0, 0, 0, h), fill="black", width=2)
        self.img_draw.line(xy=(w - 2, 0, w - 2, h), fill="black", width=2)
        self.img_draw.line(xy=(0, h - 2, w, h - 2), fill="black", width=2)
