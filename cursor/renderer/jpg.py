from __future__ import annotations

import logging
import pathlib

from PIL import Image, ImageDraw

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.renderer import PathIterator


class JpegRenderer:
    def __init__(self, folder: pathlib.Path, w: int = 1920, h: int = 1080):
        self.save_path: pathlib.Path = folder
        self.img: Image = None
        self.img_draw: ImageDraw = None

        self.image_width: int = w
        self.image_height: int = h

        self.paths: list[Path] = []
        self.positions: list[Position] = []

    def add(self, input: Collection | list[Path] | Path | Position):
        match input:
            case Path():
                self.paths.append(input)
            case Collection():
                self.paths.extend(input.paths)
            case list():
                self.paths.extend(input)
            case Position():
                self.positions.append(input)

    def render(
            self,
            paths: Collection | list[Path] | Path | None = None,
            scale: float = 1.0,
            frame: bool = False,
            thickness: int = 1,
            color: str = "black",
    ) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        if paths:
            self.add(paths)

        logging.info(f"Creating image with size=({self.image_width * scale}, {self.image_height * scale})")
        self.img = Image.new("RGB", (int(self.image_width * scale), int(self.image_height * scale)), "white")
        self.img_draw = ImageDraw.ImageDraw(self.img)

        it = PathIterator(self.paths)

        for conn in it.connections():
            start = conn[0]
            end = conn[1]

            self.img_draw.line(
                xy=(start.x * scale, start.y * scale, end.x * scale, end.y * scale),
                fill=color,
                width=thickness,
            )

        for point in self.positions:
            rad = point.properties["radius"]
            color = point.properties["color"]
            self.img_draw.ellipse(
                xy=[((point.x - rad) * scale, (point.y - rad) * scale),
                    ((point.x + rad) * scale, (point.y + rad) * scale)],
                fill=color,
                width=rad,
            )

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        fname = self.save_path / (filename + ".jpg")
        self.img = self.img.rotate(90, expand=True)
        self.img.save(fname, "JPEG")

        logging.info(f"Finished saving {fname}")

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
