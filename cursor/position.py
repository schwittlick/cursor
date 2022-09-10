from cursor.bb import BoundingBox

import numpy as np
import copy
import typing
import math


class Position:
    def __init__(self, x: float = 0.0, y: float = 0.0, timestamp: int = 0):
        self._pos = np.array([x, y], dtype="float")
        self.timestamp = timestamp

    @classmethod
    def from_tuple(cls, xy_tuple: typing.Tuple[float, float]) -> "Position":
        return cls(xy_tuple[0], xy_tuple[1])

    @property
    def x(self) -> float:
        return self._pos[0]

    @x.setter
    def x(self, v: float) -> None:
        self._pos[0] = v

    @property
    def y(self) -> float:
        return self._pos[1]

    @y.setter
    def y(self, v: float) -> None:
        self._pos[1] = v

    def astuple(self) -> tuple[float, float]:
        return tuple(self._pos)

    def arr(self) -> np.array:
        return self._pos

    def time(self) -> int:
        return self.timestamp

    def copy(self) -> "Position":
        return type(self)(
            copy.deepcopy(self.x), copy.deepcopy(self.y), copy.deepcopy(self.timestamp)
        )

    def distance(self, t: "Position") -> float:
        return np.linalg.norm(self.arr() - t.arr())

    def rot(
        self, angle: float, origin: typing.Tuple[float, float] = (0.0, 0.0)
    ) -> None:
        ox, oy = origin

        qx = ox + math.cos(angle) * (self.x - ox) - math.sin(angle) * (self.y - oy)
        qy = oy + math.sin(angle) * (self.x - ox) + math.cos(angle) * (self.y - oy)

        self.x = qx
        self.y = qy

    def translate(self, x: float, y: float) -> None:
        self._pos += (x, y)

    def scale(self, x: float, y: float) -> None:
        self._pos = np.multiply(self._pos, np.array([x, y]))

    def inside(self, bb: BoundingBox) -> bool:
        return bb.x <= self.x <= bb.x2 and bb.y <= self.y <= bb.y2

    def __eq__(self, o):
        """
        compare equality by comparing all fields
        """
        if not isinstance(o, Position):
            raise NotImplementedError

        return self.x == o.x and self.y == o.y and self.timestamp == o.timestamp

    def __lt__(self, o):
        """
        compare by timestamp
        """
        return self.timestamp < o.timestamp

    def __gt__(self, o):
        """
        compare by timestamp
        """
        return self.timestamp > o.timestamp

    def __repr__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.timestamp:.3f})"

    def __hash__(self):
        return hash(repr(self))

    def __mul__(self, other: "Position"):
        return self.arr() * other.arr()
