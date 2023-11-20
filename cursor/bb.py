from __future__ import annotations

import math


class BoundingBox:
    def __init__(self, x: float, y: float, x2: float, y2: float):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.w = math.dist([self.x], [self.x2])
        self.h = math.dist([self.y], [self.y2])

    def center(self) -> tuple[float, float]:
        center_x = (self.w / 2.0) + self.x
        center_y = (self.h / 2.0) + self.y
        return center_x, center_y

    def scale(self, fac: float) -> None:
        self.scale_x(fac)
        self.scale_y(fac)

    def scale_x(self, fac: float) -> None:
        prevw = self.w
        self.w = self.w * fac

        diff = math.dist([prevw], [self.w])
        self.x = self.x + diff / 2
        self.x2 = self.x + self.w

    def scale_y(self, fac: float) -> None:
        prevh = self.h
        self.h = self.h * fac

        diff = math.dist([prevh], [self.h])
        self.y = self.y + diff / 2
        self.y2 = self.y + self.h

    def aspect_ratio(self) -> float | math.nan:
        if self.w == 0.0 or self.h == 0.0:
            return math.nan

        return self.h / self.w

    def subdiv(self, xpieces: int, ypieces: int) -> list[BoundingBox]:
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

    def paths(self) -> list[tuple[float, float, float, float]]:
        # returns a list of lines, x1, y1, x2, y2
        paths = []
        paths.append((self.x, self.y, self.x2, self.y))
        paths.append((self.x2, self.y, self.x2, self.y2))
        paths.append((self.x2, self.y2, self.x, self.y2))
        paths.append((self.x, self.y2, self.x, self.y))
        return paths

    def __repr__(self) -> str:
        return f"BB(x={self.x:.2f}, y={self.y:.2f}, x2={self.x2:.2f}, y2={self.y2:.2f}, w={self.w:.2f}, h={self.h:.2f})"
