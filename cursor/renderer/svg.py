from __future__ import annotations

import pathlib

import svgwrite
import wasabi

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.path import Path
from cursor.renderer import PathIterator

log = wasabi.Printer()


class SvgRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path = folder
        self.dwg = None
        self.paths = Collection()
        self.bbs = []

    def render(self, paths: Collection) -> None:
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def render_bb(self, bb: BoundingBox) -> None:
        self.bbs.append(bb)

        p1 = Path()
        p1.add(bb.x, bb.y)
        p1.add(bb.x2, bb.y)
        p1.add(bb.x2, bb.y2)
        p1.add(bb.x, bb.y2)
        p1.add(bb.x, bb.y)

        self.paths.add(p1)

    def save(self, filename: str) -> None:
        bb = self.paths.bb()

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".svg")
        self.dwg = svgwrite.Drawing(fname.as_posix(), profile="tiny", size=(bb.w, bb.h))

        it = PathIterator(self.paths)
        for conn in it.connections():
            line = self.dwg.line(
                conn[0].as_tuple(),
                conn[1].as_tuple(),
                stroke_width=0.5,
                stroke="black",
            )
            self.dwg.add(line)

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        log.good(f"Finished saving {fname}")

        self.dwg.save()
