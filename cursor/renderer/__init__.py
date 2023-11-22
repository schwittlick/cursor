from __future__ import annotations

import copy
import pathlib
import typing

from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position


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

        self.paths: list[Path] = []
        self.positions: list[Position] = []

    def clear(self) -> None:
        self.paths.clear()
        self.positions.clear()

    def add(self, input: Collection | Path | Position | list[Collection] | list[Path] | list[Position]):
        match input:
            case Collection():
                self.paths.extend(input.paths)
            case Position():
                self.positions.append(input)
            case Path():
                self.paths.append(input)
            case list():
                if all(isinstance(item, Path) for item in input):
                    self.paths.extend(input)
                if all(isinstance(item, Position) for item in input):
                    self.positions.extend(input)
                if all(isinstance(item, Collection) for item in input):
                    for collection in input:
                        self.paths.extend(collection.paths)
