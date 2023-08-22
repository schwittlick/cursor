from __future__ import annotations

import copy
import typing

from cursor.collection import Collection
from cursor.position import Position


class PathIterator:
    def __init__(self, paths: Collection):
        self.paths = paths

    def points(self) -> typing.Iterator[Position]:
        for p in self.paths:
            for point in p.vertices:
                yield point

    def connections(
            self,
    ) -> typing.Iterator[typing.Tuple[Position, Position]]:
        prev = None

        for p in self.paths:
            is_first_vertex = True
            for point in p:
                if is_first_vertex:
                    prev = copy.deepcopy(point)
                    is_first_vertex = False

                    continue

                start = prev
                end = copy.deepcopy(point)
                prev = copy.deepcopy(point)

                yield start, end
