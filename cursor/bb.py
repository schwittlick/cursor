from __future__ import annotations

import math
from typing import NamedTuple, Sequence


class Point(NamedTuple):
    x: float
    y: float


class BoundingBox:
    def __init__(self, x: float, y: float, x2: float, y2: float):
        self.p1 = Point(min(x, x2), min(y, y2))
        self.p2 = Point(max(x, x2), max(y, y2))

    @property
    def w(self) -> float:
        return self.p2.x - self.p1.x

    @property
    def h(self) -> float:
        return self.p2.y - self.p1.y

    @property
    def x(self) -> float:
        return self.p1.x

    @x.setter
    def x(self, value: float) -> None:
        self.p1 = Point(value, self.p1.y)
        if value > self.p2.x:
            self.p2 = Point(value, self.p2.y)

    @property
    def y(self) -> float:
        return self.p1.y

    @y.setter
    def y(self, value: float) -> None:
        self.p1 = Point(self.p1.x, value)
        if value > self.p2.y:
            self.p2 = Point(self.p2.x, value)

    @property
    def x2(self) -> float:
        return self.p2.x

    @x2.setter
    def x2(self, value: float) -> None:
        self.p2 = Point(value, self.p2.y)
        if value < self.p1.x:
            self.p1 = Point(value, self.p1.y)

    @property
    def y2(self) -> float:
        return self.p2.y

    @y2.setter
    def y2(self, value: float) -> None:
        self.p2 = Point(self.p2.x, value)
        if value < self.p1.y:
            self.p1 = Point(self.p1.x, value)

    def center(self) -> Point:
        return Point(
            (self.p1.x + self.p2.x) / 2,
            (self.p1.y + self.p2.y) / 2
        )

    def scale(self, factor: float) -> None:
        self.scale_x(factor)
        self.scale_y(factor)

    def scale_x(self, factor: float) -> None:
        center_x = (self.p1.x + self.p2.x) / 2
        half_width = self.w / 2 * factor
        self.p1 = Point(center_x - half_width, self.p1.y)
        self.p2 = Point(center_x + half_width, self.p2.y)

    def scale_y(self, factor: float) -> None:
        center_y = (self.p1.y + self.p2.y) / 2
        half_height = self.h / 2 * factor
        self.p1 = Point(self.p1.x, center_y - half_height)
        self.p2 = Point(self.p2.x, center_y + half_height)

    def aspect_ratio(self) -> float:
        if self.w == 0:
            return math.inf
        elif self.h == 0:
            return -math.inf
        return self.h / self.w

    def area(self) -> float:
        return self.w * self.h

    def subdiv(self, x_pieces: int, y_pieces: int) -> Sequence[BoundingBox]:
        w_step = self.w / x_pieces
        h_step = self.h / y_pieces
        return [
            BoundingBox(
                self.p1.x + x * w_step,
                self.p1.y + y * h_step,
                self.p1.x + (x + 1) * w_step,
                self.p1.y + (y + 1) * h_step
            )
            for x in range(x_pieces)
            for y in range(y_pieces)
        ]

    def paths(self) -> Sequence[tuple[float, float, float, float]]:
        return [
            (self.p1.x, self.p1.y, self.p2.x, self.p1.y),
            (self.p2.x, self.p1.y, self.p2.x, self.p2.y),
            (self.p2.x, self.p2.y, self.p1.x, self.p2.y),
            (self.p1.x, self.p2.y, self.p1.x, self.p1.y),
        ]

    def contains(self, other: BoundingBox) -> bool:
        """
        Check if another BoundingBox is contained within this BoundingBox.

        Args:
            other (BoundingBox): The BoundingBox to check for containment.

        Returns:
            bool: True if the other BoundingBox is fully contained within this one, False otherwise.
        """
        return (
            self.p1.x <= other.p1.x and
            self.p1.y <= other.p1.y and
            self.p2.x >= other.p2.x and
            self.p2.y >= other.p2.y
        )

    def __repr__(self) -> str:
        return (f"BoundingBox(x={self.p1.x:.2f}, y={self.p1.y:.2f}, "
                f"x2={self.p2.x:.2f}, y2={self.p2.y:.2f}, "
                f"width={self.w:.2f}, height={self.h:.2f})")

    def __sub__(self, other: BoundingBox) -> BoundingBox:
        return BoundingBox(
            self.p1.x - other.p1.x,
            self.p1.y - other.p1.y,
            self.p2.x - other.p2.x,
            self.p2.y - other.p2.y
        )

    def __add__(self, other: BoundingBox) -> BoundingBox:
        return BoundingBox(
            self.p1.x + other.p1.x,
            self.p1.y + other.p1.y,
            self.p2.x + other.p2.x,
            self.p2.y + other.p2.y
        )
