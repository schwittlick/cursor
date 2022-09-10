import cursor.filter as cursor_filter
import cursor.bb
import cursor.misc
from cursor.position import Position
from cursor.path import Path

import numpy as np
import datetime
import pytz
import random
import hashlib
import wasabi
import copy
import typing
import operator
import time


log = wasabi.Printer()


class Collection:
    def __init__(
        self, timestamp: typing.Union[float, None] = None, name: str = "noname"
    ):
        self.__paths: typing.List[Path] = []
        self.__name = name
        if timestamp:
            self._timestamp = timestamp
        else:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            utc_timestamp = datetime.datetime.timestamp(now)
            self._timestamp = utc_timestamp

    def add(self, path: typing.Union["cursor.bb.BoundingBox", Path]) -> None:
        if isinstance(path, Path):
            if path.empty():
                return
            self.__paths.append(path)
        if isinstance(path, cursor.bb.BoundingBox):
            p = Path()
            p.add(path.x, path.y)
            p.add(path.x, path.y2)
            p.add(path.x2, path.y2)
            p.add(path.x2, path.y)
            p.add(path.x, path.y)
            self.__paths.append(p)

    def extend(self, pc: "Collection") -> None:
        new_paths = self.__paths + pc.get_all()
        self.__paths = new_paths

    def clean(self) -> None:
        """
        removes all paths with only one point
        """
        for p in self.__paths:
            p.clean()

        len_before = len(self)
        self.__paths = [path for path in self.__paths if len(path) > 2]

        log.good(
            f"PathCollection::clean: reduced path count from {len_before} to {len(self)}"
        )

    def reverse(self) -> None:
        self.__paths.reverse()

    def reversed(self) -> "Collection":
        c = copy.deepcopy(self.__paths)
        c.reverse()
        pc = Collection()
        for p in c:
            pc.add(p)

        return pc

    def limit(self) -> None:
        for p in self.__paths:
            p.limit()

    def hash(self) -> str:
        return hashlib.md5(str(self.__paths).encode("utf-8")).hexdigest()

    def empty(self) -> bool:
        if len(self.__paths) == 0:
            return True
        return False

    def copy(self) -> "Collection":
        p = Collection()
        p.__paths.extend(copy.deepcopy(self.__paths))
        return p

    def get_all(self) -> typing.List[Path]:
        return self.__paths

    def random(self) -> Path:
        return self.__getitem__(random.randint(0, self.__len__() - 1))

    def sort(self, pathsorter: "cursor_filter.Sorter", reference_path=None) -> None:
        if isinstance(pathsorter, cursor_filter.Sorter):
            pathsorter.sort(self.__paths, reference_path)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def sorted(
        self, pathsorter: "cursor_filter.Sorter", reference_path=None
    ) -> typing.List[Path]:
        if isinstance(pathsorter, cursor_filter.Sorter):
            return pathsorter.sorted(self.__paths, reference_path)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def filter(self, pathfilter: "cursor_filter.Filter") -> None:
        if isinstance(pathfilter, cursor_filter.Filter):
            pathfilter.filter(self.__paths)
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def filtered(self, pathfilter: "cursor_filter.Filter") -> "Collection":
        if isinstance(pathfilter, cursor_filter.Filter):

            pc = Collection()
            pc.__paths = pathfilter.filtered(self.__paths)
            return pc
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def __len__(self) -> int:
        return len(self.__paths)

    def __add__(self, other: typing.Union[list, "Collection"]) -> "Collection":
        if isinstance(other, Collection):
            new_paths = self.__paths + other.get_all()
            p = Collection()
            p.__paths.extend(new_paths)
            return p
        if isinstance(other, list):
            new_paths = self.__paths + other
            p = Collection()
            p.__paths.extend(new_paths)
            return p
        else:
            raise Exception(
                "You can only add another PathCollection or a list of paths"
            )

    def __repr__(self) -> str:
        return f"PathCollection({self.__name}) -> ({len(self)})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Collection):
            return NotImplemented

        if len(self) != len(other):
            return False

        if self.timestamp() != other.timestamp():
            return False

        # todo: do more in depth test

        return True

    def __iter__(self):
        for p in self.__paths:
            yield p

    def __getitem__(
        self, item: typing.Union[int, slice]
    ) -> typing.Union["Collection", Path]:
        if isinstance(item, slice):
            start, stop, step = item.indices(len(self))
            _pc = Collection()
            _pc.__paths = [self[i] for i in range(start, stop, step)]
            return _pc

        if len(self.__paths) < item + 1:
            raise IndexError(f"Index {item} too high. Maximum is {len(self.__paths)}")

        return self.__paths[item]

    def timestamp(self) -> float:
        return self._timestamp

    def get_all_line_types(self) -> typing.List[int]:
        types = []
        for p in self:
            if p.line_type not in types:
                types.append(p.line_type)

        return types

    def get_line_types(self):
        types = {}
        for type in self.get_all_line_types():
            types[type] = []

        for p in self:
            types[p.line_type].append(p)

        typed_pathcollections = {}
        for key in types:
            pc = Collection()
            pc.__paths.extend(types[key])
            typed_pathcollections[key] = pc

        return typed_pathcollections

    def layer_names(self) -> typing.List[str]:
        layers = []
        for p in self:
            if p.layer not in layers:
                layers.append(p.layer)

        return layers

    def get_layers(self):
        layers = {}
        for layer in self.layer_names():
            layers[layer] = []

        for p in self:
            layers[p.layer].append(p)

        layered_pcs = {}
        for key in layers:
            pc = Collection()
            pc.__paths.extend(layers[key])
            layered_pcs[key] = pc

        return layered_pcs

    def bb(self) -> "cursor.bb.BoundingBox":
        mi = self.min()
        ma = self.max()
        bb = cursor.bb.BoundingBox(mi[0], mi[1], ma[0], ma[1])
        if bb.x is np.nan or bb.y is np.nan or bb.x2 is np.nan or bb.y2 is np.nan:
            log.fail("SHIT")
        return bb

    def min(self) -> typing.Tuple[float, float]:
        if self.empty():
            return 0, 0

        all_chained = [point for path in self.__paths for point in path]
        minx = min(all_chained, key=lambda pos: pos.x).x
        miny = min(all_chained, key=lambda pos: pos.y).y
        return minx, miny

    def max(self) -> typing.Tuple[float, float]:
        if self.empty():
            return 0, 0

        all_chained = [point for path in self.__paths for point in path]
        maxx = max(all_chained, key=lambda pos: pos.x).x
        maxy = max(all_chained, key=lambda pos: pos.y).y
        return maxx, maxy

    def translate(self, x: float, y: float) -> None:
        for p in self.__paths:
            p.translate(x, y)

    def scale(self, x: float, y: float) -> None:
        for p in self.__paths:
            p.scale(x, y)

    def rot(self, delta: float) -> None:
        for p in self.__paths:
            p.rot(delta)

    def downsample(self, dist: float) -> None:
        for p in self.__paths:
            p.downsample(dist)

    def log(self, str) -> None:
        log.good(f"{self.__class__.__name__}: {str}")

    def move_to_origin(self):
        """
        moves pathcollection to zero origin
        after calling this the bb of the pathcollection has its x,y at 0,0
        """

        _bb = self.bb()
        if _bb.x < 0:
            self.translate(abs(_bb.x), 0.0)
        else:
            self.translate(-abs(_bb.x), 0.0)

        if _bb.y < 0:
            self.translate(0.0, abs(_bb.y))
        else:
            self.translate(0.0, -abs(_bb.y))

    def clip(self, bb: "cursor.bb.BoundingBox") -> None:
        pp = []
        for p in self.__paths:
            clipped = p.clip(bb)
            if clipped:
                for clip in clipped:
                    pp.append(clip)

        self.__paths = pp

    def fit(
        self,
        size=tuple[int, int],
        xy_factor: tuple[float, float] = (1.0, 1.0),
        padding_mm: int = None,
        padding_units: int = None,
        padding_percent: int = None,
        output_bounds: "cursor.bb.BoundingBox" = None,
        cutoff_mm=None,
        keep_aspect=False,
    ) -> None:
        """
        fits (scales and centers) a collection of paths into a bounding box. units can be in pixels or mm
        """
        _bb = self.bb()

        # move into positive area
        if _bb.x != 0.0 and _bb.y != 0.0:
            self.move_to_origin()

        _bb = self.bb()

        width = size[0]
        height = size[1]

        padding_x = 0
        padding_y = 0

        if padding_mm is not None and padding_units is None and padding_percent is None:
            padding_x = padding_mm * xy_factor[0]
            padding_y = padding_mm * xy_factor[1]

            # multiply both tuples
            _size = tuple(_ * r for _, r in zip(size, xy_factor))
            width = _size[0]
            height = _size[1]

        if padding_mm is None and padding_units is not None and padding_percent is None:
            padding_x = padding_units
            padding_y = padding_units

        if padding_mm is None and padding_units is None and padding_percent is not None:
            padding_x = abs(width * padding_percent)
            padding_y = abs(height * padding_percent)

        # scaling
        _bb = self.bb()

        _w = _bb.w
        if _w == 0.0:
            _w = 0.001
        _h = _bb.h
        if _h == 0.0:
            _h = 0.001
        xscale = (width - padding_x * 2.0) / _w
        yscale = (height - padding_y * 2.0) / _h

        if keep_aspect:
            if xscale > yscale:
                xscale = yscale
            else:
                yscale = xscale

        log.info(f"{self.__class__.__name__}: fit: scaled by {xscale:.2f} {yscale:.2f}")
        self.scale(xscale, yscale)

        # centering
        _bb = self.bb()
        paths_center = _bb.center()

        output_bounds_center = Position(width / 2.0, height / 2.0)

        if output_bounds:
            output_bounds_center = output_bounds.center()

        diff = (
            output_bounds_center.x - paths_center.x,
            output_bounds_center.y - paths_center.y,
        )

        log.info(
            f"{self.__class__.__name__}: fit: translated by {diff[0]:.2f} {diff[1]:.2f}"
        )

        self.translate(diff[0], diff[1])

        if cutoff_mm is not None:
            cuttoff_margin_diff = padding_mm - cutoff_mm

            if cuttoff_margin_diff > 0:
                return

            cuttoff_margin_diff_x = cuttoff_margin_diff * xy_factor[0]
            cuttoff_margin_diff_y = cuttoff_margin_diff * xy_factor[1]

            cutoff_bb = self.bb()
            cutoff_bb.x -= cuttoff_margin_diff_x
            cutoff_bb.x2 += cuttoff_margin_diff_x
            cutoff_bb.y -= cuttoff_margin_diff_y
            cutoff_bb.y2 += cuttoff_margin_diff_y

            self.__paths = [x for x in self.__paths if cutoff_bb.inside(x)]

    def reorder_tsp(self) -> None:
        """
        use this with caution, it works for 20 paths, but will run
        out of memory for hundreds of points.. this implementation is
        kind of useless here, but i'll leave it here for the moment..
        you never know.
        """
        import mlrose_hiive as mlrose
        import numpy as np

        dist_list = []

        for i in range(len(self)):
            for j in range(len(self)):
                if j is not i:
                    a = self[i].bb().center()
                    a = np.array(a, dtype=float)
                    b = self[j].bb().center()
                    b = np.array(b, dtype=float)
                    dist = np.linalg.norm(a - b)
                    if dist == 0.0:
                        dist = 0.01
                    dist_list.append((i, j, dist))

        fitness_dists = mlrose.TravellingSales(distances=dist_list)
        problem_fit = mlrose.TSPOpt(
            length=len(self), fitness_fn=fitness_dists, maximize=False
        )
        best_state, best_fitness, fitness_curve = mlrose.genetic_alg(
            problem_fit, random_state=2
        )
        self.__paths[:] = [self.__paths[i] for i in best_state]

    def reorder_quadrants(self, xq: int, yq: int) -> None:
        if xq < 2 and yq < 2:
            return

        def calc_bb(x: int, y: int) -> cursor.bb.BoundingBox:
            big_bb = self.bb()

            new_width = big_bb.w / xq
            new_height = big_bb.h / yq

            _x = x * new_width
            _y = y * new_height

            new_bb = cursor.bb.BoundingBox(_x, _y, _x + new_width, _y + new_height)

            return new_bb

        bbs = {}
        bbcounter = 0
        for y in range(yq):
            if y % 2 == 0:
                for x in range(xq):
                    bb = calc_bb(x, y)
                    bbs[bbcounter] = bb
                    bbcounter += 1
            else:
                for x in reversed(range(xq)):
                    bb = calc_bb(x, y)
                    bbs[bbcounter] = bb
                    bbcounter += 1

        def _count_inside(_bb: cursor.bb.BoundingBox, _pa: Path) -> int:
            c = 0
            for _p in _pa:
                if _bb.inside(_p):
                    c += 1
            return c

        start_benchmark = time.time()

        best = {}

        for p in self:
            bbcounter = 0
            mapping = {}
            for y in range(yq):
                if y % 2 == 0:
                    for x in range(xq):
                        bb = bbs[bbcounter]
                        inside = _count_inside(bb, p)
                        mapping[bbcounter] = inside
                        bbcounter += 1
                else:
                    for x in reversed(range(xq)):
                        bb = bbs[bbcounter]
                        inside = _count_inside(bb, p)
                        mapping[bbcounter] = inside
                        bbcounter += 1
            best_bb = max(mapping.items(), key=operator.itemgetter(1))[0]
            best[p] = best_bb

        ss = dict(sorted(best.items(), key=lambda item: item[1]))

        elapsed = time.time() - start_benchmark
        log.info(
            f"reorder_quadrants with x={xq} y={yq} took {round(elapsed * 1000)}ms."
        )

        self.__paths = list(ss.keys())