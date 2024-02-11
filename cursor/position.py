from __future__ import annotations

import copy
import math
from decimal import *
import numpy as np

from cursor.bb import BoundingBox

getcontext().prec = 4


class Position:
    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            timestamp: int = 0,
            properties: dict | None = None
    ):
        if properties is None:
            properties = {}
        else:
            pass
        self._pos = np.array([Decimal(x), Decimal(y)], dtype=Decimal)
        self.timestamp = timestamp
        self.properties = properties

    @classmethod
    def from_tuple(cls, xy_tuple: tuple[float, float]) -> Position:
        return cls(xy_tuple[0], xy_tuple[1])

    @classmethod
    def from_array(cls, arr: np.array) -> Position:
        return cls(arr[0], arr[1])

    @property
    def x(self) -> float:
        return float(self._pos[0])

    @x.setter
    def x(self, v: float) -> None:
        self._pos[0] = Decimal(v)

    @property
    def y(self) -> float:
        return float(self._pos[1])

    @y.setter
    def y(self, v: float) -> None:
        self._pos[1] = Decimal(v)

    def as_tuple(self) -> tuple[float, float]:
        return self.x, self.y

    def as_array(self) -> np.array:
        return self._pos.astype(float)

    def time(self) -> int:
        return self.timestamp

    def copy(self) -> Position:
        return type(self)(
            copy.deepcopy(self.x), copy.deepcopy(self.y), copy.deepcopy(self.timestamp)
        )

    def distance(self, t: Position | np.ndarray | tuple[float, float]) -> float:
        func = np.linalg.norm
        match t:
            case Position():
                return func(self.as_array() - t.as_array())
            case np.ndarray():
                return func(self.as_array() - t)
            case tuple():
                return func(self.as_array() - np.asarray(t))

    def distance_squared(self, t: Position | np.ndarray | tuple[float, float]) -> float:
        def squared_euclidean_distance(p1: tuple, p2: tuple) -> float:
            # dx = p1.x - p2.x
            # dy = p1.y - p2.y
            # return dx * dx + dy * dy
            return sum((i - j) ** 2 for i, j in zip(p1, p2))

        match t:
            case Position():
                return squared_euclidean_distance(self.as_tuple(), t.as_tuple())
            case tuple():
                return squared_euclidean_distance(self.as_tuple(), t)

    def rot(
            self, angle: float, origin: tuple[float, float] = (0.0, 0.0)
    ) -> None:
        ox, oy = origin

        qx = ox + math.cos(angle) * (self.x - ox) - math.sin(angle) * (self.y - oy)
        qy = oy + math.sin(angle) * (self.x - ox) + math.cos(angle) * (self.y - oy)

        self.x = qx
        self.y = qy

    def translate(self, x: float, y: float) -> None:
        self._pos += Decimal(x), Decimal(y)

    def translated(self, x: float, y: float) -> Position:
        _p = self.copy()
        _p.translate(x, y)
        return _p

    def scale(self, x: float, y: float) -> None:
        self._pos = np.multiply(self._pos, [Decimal(x), Decimal(y)])
        #self._pos *=

    def scaled(self, x: float, y: float) -> Position:
        _p = self.copy()
        _p.scale(x, y)
        return _p

    def inside(self, bb: BoundingBox) -> bool:
        return bb.x <= self.x <= bb.x2 and bb.y <= self.y <= bb.y2

    def __eq__(self, o: Position) -> bool:
        """
        compare equality by comparing all fields
        """

        return self.x == o.x and self.y == o.y and self.timestamp == o.timestamp

    def __lt__(self, o: Position) -> bool:
        """
        compare by timestamp
        """
        return self.timestamp < o.timestamp

    def __gt__(self, o: Position) -> bool:
        """
        compare by timestamp
        """
        return self.timestamp > o.timestamp

    def __repr__(self) -> str:
        return f"({self.x:.3f}, {self.y:.3f}, {self.timestamp:.3f}, {self.properties})"

    def __hash__(self) -> int:
        return hash(repr(self))

    def __mul__(self, o: Position) -> np.array:
        return self.as_array() * o.as_array()

    def __sub__(self, o: Position) -> Position:
        subtracted = np.subtract(o.as_array(), self.as_array())
        return Position.from_array(subtracted)

    def __add__(self, o: Position) -> Position:
        added = np.add(o.as_array(), self.as_array())
        return Position.from_array(added)
