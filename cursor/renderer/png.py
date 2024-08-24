import cairo
import logging
import pathlib
from typing import Tuple

from cursor.bb import BoundingBox
from cursor.properties import Property
from cursor.position import Position
from cursor.renderer import BaseRenderer


class CairoRenderer(BaseRenderer):
    def __init__(self, folder: pathlib.Path, w: int = 1920, h: int = 1080):
        super().__init__(folder)

        logging.debug(f"Creating image with size=({w}, {h})")
        self._background = (0, 0, 0)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.surface)

        # Clear the surface with the background color
        self.background(self._background)

    def background(self, color: Tuple[int, int, int]):
        self._background = color
        self.ctx.set_source_rgb(*[c / 255.0 for c in color])
        self.ctx.paint()

    def render(self, scale: float = 1.0, frame: bool = False) -> None:
        self.render_all_paths(scale=scale)
        self.render_all_points(scale=scale)

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".png")
        self.surface.write_to_png(str(fname))

        logging.info(f"Finished saving {fname.name}")
        logging.info(f"in {self.save_path}")

    def rotate(self, degree: float = 90) -> None:
        # Cairo doesn't have a direct rotate function for surfaces, so we'll need to create a new surface
        w, h = self.surface.get_width(), self.surface.get_height()
        new_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, h, w)
        new_ctx = cairo.Context(new_surface)

        new_ctx.translate(h / 2, w / 2)
        new_ctx.rotate(degree * (3.14159 / 180))
        new_ctx.translate(-w / 2, -h / 2)
        new_ctx.set_source_surface(self.surface)
        new_ctx.paint()

        self.surface = new_surface
        self.ctx = new_ctx

    def render_bb(self, bb: BoundingBox) -> None:
        self.ctx.set_source_rgb(0, 0, 0)  # Black color
        self.ctx.set_line_width(2)
        self.ctx.rectangle(bb.x, bb.y, bb.x2 - bb.x, bb.y2 - bb.y)
        self.ctx.stroke()

    def render_frame(self) -> None:
        w, h = self.surface.get_width(), self.surface.get_height()
        self.ctx.set_source_rgb(0, 0, 0)  # Black color
        self.ctx.set_line_width(2)
        self.ctx.rectangle(0, 0, w, h)
        self.ctx.stroke()

    def render_all_paths(self, scale: float = 1.0):
        for path in self.collection:
            path.scale(scale, scale)
            points = path.as_tuple_list()
            r, g, b = [c / 255.0 for c in path.color]
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.set_line_width(path.width)
            self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)

            self.ctx.move_to(*points[0])
            for point in points[1:]:
                self.ctx.line_to(*point)
            self.ctx.stroke()

    def render_points(self, points: list[Position], scale: float):
        for point in points:
            rad = point.properties[Property.RADIUS]
            r, g, b = [c / 255.0 for c in point.properties[Property.COLOR]]

            self.ctx.set_source_rgba(r, g, b, 1)
            self.ctx.arc(point.x * scale, point.y * scale, rad * scale, 0, 2 * 3.14159)
            self.ctx.fill()

            if "outline" in point.properties:
                or_, og, ob = [c / 255.0 for c in point.properties["outline"]]
                self.ctx.set_source_rgba(or_, og, ob, 1)
                self.ctx.set_line_width(rad)
                self.ctx.arc(point.x * scale, point.y * scale, rad * scale, 0, 2 * 3.14159)
                self.ctx.stroke()

    def render_all_points(self, scale: float = 1.0):
        # Cairo doesn't have built-in Gaussian blur, so we'll skip the blurring for now
        self.render_points(self.positions, scale)

# Note: Gaussian blur is not directly supported in Cairo, so that part of the functionality is omitted
