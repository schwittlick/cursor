import pathlib
import svgwrite
import logging

from cursor.properties import Property
from cursor.renderer import BaseRenderer


class SvgRenderer(BaseRenderer):
    def __init__(self, folder: pathlib.Path, w: int, h: int):
        super().__init__(folder)
        self.dwg = svgwrite.Drawing("", profile="tiny", size=(w, h))

    def render(self, scale: float = 1.0) -> None:
        self.render_all_paths(scale=scale)
        self.render_all_points(scale=scale)

    def render_all_paths(self, scale: float = 1.0):
        for path in self.collection:
            path.scale(scale, scale)
            points = path.as_tuple_list()
            color = path.properties[Property.COLOR]
            width = path.properties[Property.WIDTH]
            str_points = [tuple(map(str, p)) for p in points]
            self.dwg.add(self.dwg.polyline(str_points, stroke_width=width, stroke=f"rgb{color}"))

    def render_all_points(self, scale: float = 1.0):
        for point in self.positions:
            point.scale(scale, scale)
            color = point.properties[Property.COLOR]
            width = point.properties[Property.WIDTH]
            str_point = tuple(map(str, point.as_tuple()))

            self.dwg.add(self.dwg.circle(str_point, r=width, stroke_width=width, stroke=f"rgb{color}"))

    def save(self, filename: str) -> None:
        fname = self.save_path / (filename + ".svg")
        self.dwg.filename = fname.as_posix()
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        self.dwg.save(pretty=True)

        logging.info(f"Finished saving {fname.name}")
        logging.info(f"in {self.save_path}")
