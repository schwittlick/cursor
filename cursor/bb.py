from __future__ import annotations

import math
import typing


class BoundingBox:
    def __init__(self, x: float, y: float, x2: float, y2: float):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.w = math.dist([self.x], [self.x2])
        self.h = math.dist([self.y], [self.y2])

    def center(self) -> typing.Tuple[float, float]:
        center_x = (self.w / 2.0) + self.x
        center_y = (self.h / 2.0) + self.y
        return center_x, center_y

    def scale(self, fac: float) -> None:
        self.w = self.w * fac
        self.h = self.h * fac
        self.x = self.x + self.w / 2
        self.y = self.y + self.h / 2
        self.x2 = self.x + self.w
        self.y2 = self.y + self.h

    def subdiv(self, xpieces: int, ypieces: int) -> typing.List[BoundingBox]:
        bbs = []
        for x in range(xpieces):
            for y in range(ypieces):
                w = self.x2 / xpieces
                h = self.y2 / ypieces
                xoff = x * w + self.x
                yoff = y * h + self.y
                bb = BoundingBox(xoff, yoff, xoff + w, yoff + h)
                bbs.append(bb)

        return bbs

    def paths(self) -> typing.List[typing.Tuple[float, float, float, float]]:
        # returns a list of lines, x1, y1, x2, y2
        paths = []
        paths.append((self.x, self.y, self.x2, self.y))
        paths.append((self.x2, self.y, self.x2, self.y2))
        paths.append((self.x2, self.y2, self.x, self.y2))
        paths.append((self.x, self.y2, self.x, self.y))
        return paths

    def __repr__(self) -> str:
        return f"BB(x={self.x}, y={self.y}, x2={self.x2}, y2={self.y2}, w={self.w}, h={self.h})"
