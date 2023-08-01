from __future__ import annotations

import copy
import math
import typing

import numpy as np

from cursor.bb import BoundingBox


class Position:
    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            timestamp: int = 0,
            properties: typing.Union[None, dict] = None
    ):
        if properties is None:
            properties = {}
        self._pos = np.array([x, y], dtype=float)
        self.timestamp = timestamp
        self.properties = properties

    @classmethod
    def from_tuple(cls, xy_tuple: typing.Tuple[float, float]) -> Position:
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

    def as_tuple(self) -> tuple[float, float]:
        return tuple(self._pos)

    def as_array(self) -> np.array:
        return self._pos

    def time(self) -> int:
        return self.timestamp

    def copy(self) -> Position:
        return type(self)(
            copy.deepcopy(self.x), copy.deepcopy(self.y), copy.deepcopy(self.timestamp)
        )

    def distance(self, t: typing.Union[Position, np.ndarray, tuple[float, float]]) -> float:
        func = np.linalg.norm
        if isinstance(t, Position):
            return func(self.as_array() - t.as_array())
        elif isinstance(t, np.ndarray):
            return func(self.as_array() - t)
        elif isinstance(t, tuple):
            return func(self.as_array() - np.asarray(t))

    def rot(
            self, angle: float, origin: tuple[float, float] = (0.0, 0.0)
    ) -> None:
        ox, oy = origin

        qx = ox + math.cos(angle) * (self.x - ox) - math.sin(angle) * (self.y - oy)
        qy = oy + math.sin(angle) * (self.x - ox) + math.cos(angle) * (self.y - oy)

        self.x = qx
        self.y = qy

    def translate(self, x: float, y: float) -> None:
        self._pos += x, y

    def scale(self, x: float, y: float) -> None:
        self._pos *= x, y

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
        return f"({self.x:.3f}, {self.y:.3f}, {self.timestamp:.3f}, {self.properties})"

    def __hash__(self):
        return hash(repr(self))

    def __mul__(self, other: Position):
        return self.as_array() * other.as_array()
