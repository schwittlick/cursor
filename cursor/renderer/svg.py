from __future__ import annotations

import pathlib

import svgwrite
import wasabi

from cursor.properties import Property
from cursor.renderer import PathIterator, BaseRenderer

log = wasabi.Printer()


class SvgRenderer(BaseRenderer):
    def __init__(self, folder: pathlib.Path, w: int, h: int):
        super().__init__(folder)
        self.dwg = svgwrite.Drawing("", profile="tiny", size=(w, h))

    def render(self, scale: float = 1.0, frame: bool = False) -> None:
        self.render_all_paths(scale=scale)
        # self.render_all_points(scale=scale)

        # it = PathIterator(self.paths)
        # for conn in it.connections():
        #    line = self.dwg.line(
        #        conn[0].as_tuple(),
        #        conn[1].as_tuple(),
        #        stroke_width=0.5,
        #        stroke="black",
        #    )
        #    self.dwg.add(line)

    def render_all_paths(self, scale: float = 1.0):
        for path in self.paths:
            path.scale(scale, scale)
            points = path.as_tuple_list()
            color = path.properties[Property.COLOR]
            width = path.properties[Property.WIDTH]
            int_points = [tuple(map(str, p)) for p in points]
            self.dwg.add(self.dwg.polyline(int_points, stroke_width=width, stroke=f"rgb{color}"))

    def save(self, filename: str) -> None:
        self.dwg.filename = (self.save_path / (filename + ".svg")).as_posix()
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        self.dwg.save(pretty=True)

        log.good(f"Finished saving {self.dwg.filename}")
