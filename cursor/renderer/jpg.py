from __future__ import annotations

import logging
import pathlib

from PIL import Image, ImageDraw, ImageFilter

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.path import Path, Property
from cursor.position import Position


class JpegRenderer:
    def __init__(self, folder: pathlib.Path, w: int = 1920, h: int = 1080):
        self.save_path: pathlib.Path = folder

        logging.info(
            f"Creating image with size=({w}, {h})"
        )
        self._background = (0, 0, 0)
        self.img: Image = Image.new("RGBA", (w, h), self._background)
        self.img_draw = ImageDraw.ImageDraw(self.img)

        self.paths: list[Path] = []
        self.positions: list[Position] = []

    def background(self, color: tuple[int, int, int]):
        self._background = color
        self.img_draw.rectangle((0, 0, self.img.width, self.img.height), fill=self._background)

    def add(self, input: Collection | Path | Position | list[Collection] | list[Path] | list[Position]):
        match input:
            case Collection():
                self.paths.extend(input.paths)
            case Position():
                self.positions.append(input)
            case Path():
                self.paths.append(input)
            case list():
                if all(isinstance(item, Path) for item in input):
                    self.paths.extend(input)
                if all(isinstance(item, Position) for item in input):
                    self.positions.extend(input)
                if all(isinstance(item, Collection) for item in input):
                    for collection in input:
                        self.paths.extend(collection.paths)

    def render(self, scale: float = 1.0, frame: bool = False) -> None:
        self.render_all_paths(scale=scale)
        self.render_all_points(scale=scale)

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".jpg")
        self.img.save(fname, "JPEG")

        logging.info(f"Finished saving {fname}")

    def rotate(self, degree: float = 90) -> None:
        self.img = self.img.rotate(degree, expand=True)

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

    def render_all_paths(self, scale: float = 1.0):
        for path in self.paths:
            path.scale(scale, scale)
            points = path.as_tuple_list()
            color = path.properties[Property.COLOR]
            width = path.properties[Property.WIDTH]
            self.img_draw.line(points, fill=color, width=width, joint="curve")

    def render_points(self, points: list[Position], scale: float) -> Image:
        img: Image = Image.new("RGBA", (self.img.width, self.img.height),
                               (self._background[0], self._background[1], self._background[2], 0))
        img_draw = ImageDraw.ImageDraw(img)

        for point in points:
            rad = point.properties["radius"]
            color = point.properties["color"]

            if "outline" in point.properties.keys():
                outline = point.properties["outline"]
                img_draw.ellipse(
                    xy=[
                        ((point.x - rad) * scale, (point.y - rad) * scale),
                        ((point.x + rad) * scale, (point.y + rad) * scale),
                    ],
                    fill=color,
                    outline=outline,
                    width=int(rad),
                )
            else:
                img_draw.ellipse(
                    xy=[
                        ((point.x - rad) * scale, (point.y - rad) * scale),
                        ((point.x + rad) * scale, (point.y + rad) * scale),
                    ],
                    fill=color)
        return img

    def render_all_points(self, scale: float = 1.0):
        do_blur = {}
        dont_blur = []

        for point in self.positions:
            if "blur" in point.properties.keys():
                rad = point.properties["radius"]
                if rad not in do_blur.keys():
                    do_blur[point.properties["radius"]] = []
                do_blur[rad].append(point)
            else:
                dont_blur.append(point)

        if len(do_blur) > 0:
            _blurred = []
            for k, v in do_blur.items():
                _k = k / 4 * scale
                _blurred.append(self.render_points(v, scale).filter(ImageFilter.GaussianBlur(radius=_k / 2)))

            base = _blurred[0]
            for image in _blurred[1:]:
                base = Image.alpha_composite(base, image)
            _not_blurred = self.render_points(dont_blur, scale)
            _not_blurred = Image.alpha_composite(self.img, _not_blurred)
            self.img = Image.alpha_composite(_not_blurred, base).convert("RGB")
        else:
            # TODO: FIX HERE
            self.img = self.render_points(dont_blur, scale).convert("RGB")
            #self.img = Image.alpha_composite(img_out, self.img).convert("RGB")
