from __future__ import annotations

import numpy as np


class BoundingBox:
    def __init__(self, x: float, y: float, x2: float, y2: float):
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2
        self.w = np.linalg.norm(self.x - self.x2)
        self.h = np.linalg.norm(self.y - self.y2)

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

        diff = np.linalg.norm(prevw - self.w)
        self.x = self.x + diff / 2
        self.x2 = self.x + self.w

    def scale_y(self, fac: float) -> None:
        prevh = self.h
        self.h = self.h * fac

        diff = np.linalg.norm(prevh - self.h)
        self.y = self.y + diff / 2
        self.y2 = self.y + self.h

    def aspect_ratio(self) -> float | np.inf:
        if self.w == 0.0:
            return np.inf
        elif self.h == 0.0:
            return -np.inf

        return self.h / self.w

    def area(self) -> float:
        return self.w * self.h

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

    def __sub__(self, o: BoundingBox) -> BoundingBox:
        return BoundingBox(self.x - o.x, self.y - o.y, self.x2 - o.x2, self.y2 - o.y2)
