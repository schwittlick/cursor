import logging
import pathlib

from PIL import Image, ImageDraw, ImageFilter

from cursor.bb import BoundingBox
from cursor.properties import Property
from cursor.position import Position
from cursor.renderer import BaseRenderer


class JpegRenderer(BaseRenderer):
    def __init__(self, folder: pathlib.Path, w: int = 1920, h: int = 1080):
        super().__init__(folder)

        logging.info(
            f"Creating image with size=({w}, {h})"
        )
        self._background = (0, 0, 0)
        self.img: Image = Image.new("RGBA", (w, h), self._background)
        self.img_draw = ImageDraw.ImageDraw(self.img)

    def background(self, color: tuple[int, int, int]):
        self._background = color
        self.img_draw.rectangle((0, 0, self.img.width, self.img.height), fill=self._background)

    def render(self, scale: float = 1.0, frame: bool = False) -> None:
        self.render_all_paths(scale=scale)
        self.render_all_points(scale=scale)

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".png")
        self.img.save(fname, "png")

        logging.info(f"Finished saving {fname.name}")
        logging.info(f"in {self.save_path}")

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
            self.img_draw.line(points, fill=path.color, width=path.width, joint="curve")

    def render_points(self, points: list[Position], scale: float) -> Image:
        img: Image = Image.new("RGBA", (self.img.width, self.img.height),
                               (self._background[0], self._background[1], self._background[2], 0))
        img_draw = ImageDraw.ImageDraw(img)

        for point in points:
            rad = point.properties[Property.RADIUS]  # for c92 use .value here and in the line below
            color = point.properties[Property.COLOR]

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

        # separate points by blur radius
        for point in self.positions:
            if "blur" in point.properties.keys():
                rad = point.properties[Property.RADIUS]  # for c92 this should be "radius"
                if rad not in do_blur.keys():
                    do_blur[point.properties[Property.RADIUS]] = []
                do_blur[rad].append(point)
            else:
                dont_blur.append(point)

        if len(do_blur) > 0:
            _blurred = []
            # blur each "layer" with its own radius and compose all afterwards
            # this is kinda memory heavy but it's necessary
            for k, v in do_blur.items():
                _k = k / 4 * scale
                blur_filter = ImageFilter.GaussianBlur(radius=_k / 2)
                _blurred.append(self.render_points(v, scale).filter(blur_filter))

            base = _blurred[0]
            for image in _blurred[1:]:
                base = Image.alpha_composite(base, image)
            _not_blurred = self.render_points(dont_blur, scale)
            _not_blurred = Image.alpha_composite(self.img, _not_blurred)
            self.img = Image.alpha_composite(_not_blurred, base).convert("RGB")
        else:
            img_out = self.render_points(dont_blur, scale)
            self.img = Image.alpha_composite(self.img, img_out).convert("RGB")
