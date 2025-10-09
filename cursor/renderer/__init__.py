from __future__ import annotations

import copy
import pathlib
import typing

from ..collection import Collection
from ..path import Path
from ..position import Position


class PathIterator:
    def __init__(self, paths: Collection | list[Path]):
        self.paths = paths

    def points(self) -> typing.Iterator[Position]:
        for p in self.paths:
            for point in p.vertices:
                yield point

    def connections(
        self,
    ) -> typing.Iterator[tuple[Position, Position]]:
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


class BaseRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path: pathlib.Path = folder

        self.collection: Collection = Collection()
        self.positions: list[Position] = []

    def clear(self) -> None:
        self.collection.clear()
        self.positions.clear()

    def add(self, input: Collection | Path | Position | list[Collection] | list[Path] | list[Position]):
        if isinstance(input, Collection):
            self.collection.paths.extend(input.paths)
        elif isinstance(input, Position):
            self.positions.append(input)
        elif isinstance(input, Path):
            self.collection.add(input)
        elif isinstance(input, list):
            for item in input:
                if isinstance(item, Path):
                    self.collection.add(item)
                elif isinstance(item, Position):
                    self.positions.append(item)
                elif isinstance(item, Collection):
                    self.collection += item
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")
