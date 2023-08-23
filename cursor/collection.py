from __future__ import annotations

import copy
import datetime
import hashlib
import itertools
import operator
import pickle
import random
import time
import typing
from functools import reduce

import numpy as np
import pandas as pd
import pytz
import shapely
import wasabi
from matplotlib import pyplot as plt
from shapely import LineString, Polygon, intersection_all
from skimage.transform import estimate_transform
from scipy import spatial
from sko.GA import GA_TSP

from cursor.bb import BoundingBox
from cursor.data import DataDirHandler
from cursor.filter import Filter
from cursor.misc import apply_matrix
from cursor.path import Path
from cursor.position import Position
from cursor.sorter import Sorter

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

    @property
    def paths(self):
        return self.__paths

    def __len__(self) -> int:
        return len(self.__paths)

    def __add__(self, other: typing.Union[list, Collection]) -> Collection:
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
            raise Exception("You can only add another Collection or a list of paths")

    def __repr__(self) -> str:
        tuples = [pa.as_tuple_list() for pa in self]
        return f"PathCollection({self.__name}) -> ({len(self)})\n{tuples}"

    def __eq__(self, other: Collection) -> bool:
        if not isinstance(other, Collection):
            return NotImplemented

        if len(self) != len(other):
            return False

        for i in range(len(self)):
            if self[i] == other[i]:
                continue

            return False

        return True

    def __iter__(self):
        for p in self.__paths:
            yield p

    def __getitem__(
            self, item: typing.Union[int, slice]
    ) -> typing.Union[Collection, Path]:
        if isinstance(item, slice):
            start, stop, step = item.indices(len(self))
            _pc = Collection()
            _pc.__paths = [self[i] for i in range(start, stop, step)]
            return _pc

        if len(self.__paths) < item + 1:
            raise IndexError(f"Index {item} too high. Maximum is {len(self.__paths)}")

        return self.__paths[item]

    def save_pickle(self, fname: str) -> None:
        fn = DataDirHandler().pickles() / fname
        file_to_store = open(fn.as_posix(), "wb")
        pickle.dump(self, file_to_store)
        log.info(f"Saved {fn.as_posix()}")

    @staticmethod
    def from_pickle(fname: str) -> Collection:
        fn = DataDirHandler().pickles() / fname
        with open(fn, "rb") as file:
            return pickle.load(file)

    @staticmethod
    def from_tuples(tuples: list[list[tuple]]) -> Collection:
        c = Collection()
        for tup in tuples:
            c.add(Path.from_tuple_list(tup))
        return c

    @staticmethod
    def from_path_list(paths: list[Path]) -> Collection:
        c = Collection()
        for p in paths:
            c.add(p)
        return c

    def add(self, path: typing.Union[BoundingBox, Path, typing.List[Path]]) -> None:
        if isinstance(path, Path):
            if path.empty():
                return
            self.__paths.append(path)
        if isinstance(path, list):
            self.__paths.extend(path)
        if isinstance(path, BoundingBox):
            p = Path().from_tuple_list(
                [
                    (path.x, path.y),
                    (path.x, path.y2),
                    (path.x2, path.y2),
                    (path.x2, path.y),
                    (path.x, path.y),
                ]
            )
            self.__paths.append(p)

    def pop(self, idx: int) -> Path:
        return self.__paths.pop(idx)

    def as_array(self) -> np.array:
        return np.array([p.as_array() for p in self.__paths], dtype=object)

    def as_dataframe(self):
        df = pd.concat([p.as_dataframe() for p in self.__paths], axis=1)
        return df

    def point_count(self) -> int:
        return sum([len(p) for p in self])

    def extend(self, pc: Collection) -> None:
        new_paths = self.__paths + pc.get_all()
        self.__paths = new_paths

    def clear(self) -> None:
        self.__paths.clear()

    def clean(self) -> None:
        """
        removes all paths with only one point
        """
        [p.clean() for p in self.__paths]

        len_before = len(self)
        self.__paths = [path for path in self.__paths if len(path) > 1]

        log.good(
            f"PathCollection::clean: reduced path count from {len_before} to {len(self)}"
        )

    def merge(self) -> Path:
        pa = Path()

        for p in self:
            for poi in p:
                pa.add_position(poi)

        return pa

    def rotate_into_bb(self, target_bb: BoundingBox) -> Collection:
        merged_into_path = self.merge()
        if merged_into_path.is_1_dimensional():
            log.warn("Didn't rotate, bc path is 1-dimensional.")
            return self

        line = LineString(merged_into_path.as_tuple_list())
        rect = line.minimum_rotated_rectangle

        target_poly = Polygon([[0, 0], [target_bb.x2, 0], [target_bb.x2, target_bb.y2], [0, target_bb.y2], [0, 0]])

        src = np.array(rect.exterior.coords)
        dst = np.array(target_poly.exterior.coords)
        matrix = estimate_transform('similarity', src, dst).params
        matrix = np.append(matrix, [[0, 0, 0]], axis=0).flatten()

        coll = Collection()
        for path in self:
            tup = apply_matrix(path.as_tuple_list(), matrix)
            pa = Path()
            for i, t in enumerate(tup):
                newpos = Position.from_tuple(t)
                newpos.properties = path[i].properties
                pa.add_position(newpos)
            pa.properties = path.properties
            coll.add(pa)
        return coll

    def reverse(self) -> None:
        self.__paths.reverse()

    def reversed(self) -> Collection:
        c = copy.deepcopy(self.__paths)
        c.reverse()
        pc = Collection()
        [pc.add(p) for p in c]

        return pc

    def limit(self) -> None:
        [p.limit() for p in self.__paths]

    def hash(self) -> str:
        return hashlib.md5(str(self.__paths).encode("utf-8")).hexdigest()

    def empty(self) -> bool:
        if len(self.__paths) == 0:
            return True
        return False

    def copy(self) -> Collection:
        p = Collection()
        p.__paths.extend(copy.deepcopy(self.__paths))
        return p

    def get_all(self) -> typing.List[Path]:
        return self.__paths

    def random(self) -> Path:
        return random.choice(self.__paths)

    def sort(self, pathsorter: Sorter, reference_path: Path = None) -> None:
        if isinstance(pathsorter, Sorter):
            pathsorter.sort(self.__paths, reference_path)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def sorted(
            self, pathsorter: Sorter, reference_path: Path = None
    ) -> typing.List[Path]:
        if isinstance(pathsorter, Sorter):
            return pathsorter.sorted(self.__paths, reference_path)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def filter(self, pathfilter: Filter) -> None:
        if isinstance(pathfilter, Filter):
            pathfilter.filter(self.__paths)
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def filtered(self, pathfilter: Filter) -> Collection:
        if isinstance(pathfilter, Filter):

            pc = Collection()
            pc.__paths = pathfilter.filtered(self.__paths)
            return pc
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def timestamp(self) -> float:
        return self._timestamp

    def inside(self, bb: BoundingBox) -> bool:
        for path in self:
            for p in path:
                if not p.inside(bb):
                    return False
        return True

    def get_all_line_types(self) -> typing.List[int]:
        types = []
        for p in self:
            if p.line_type not in types:
                types.append(p.line_type)

        return types

    def intersections(self) -> list[Position]:
        permutations = list(itertools.combinations(self.paths, 2))
        points = []

        for combination in permutations:
            linestrings = [LineString(combination[0].as_tuple_list()), LineString(combination[1].as_tuple_list())]
            intersections = intersection_all(linestrings)

            if isinstance(intersections, shapely.geometry.Point):
                points.append(Position(intersections.x, intersections.y))
            if isinstance(intersections, shapely.geometry.MultiPoint):
                for point in intersections.geoms:
                    points.append(Position(point.x, point.y))

        return points

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

    def bb(self) -> BoundingBox:
        mi = self.min()
        ma = self.max()
        bb = BoundingBox(mi[0], mi[1], ma[0], ma[1])
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

    def transform(self, out: BoundingBox):
        bb = self.bb()
        for p in self:
            p.transform(bb, out)

    def translate(self, x: float, y: float) -> None:
        [p.translate(x, y) for p in self]

    def scale(self, x: float, y: float) -> None:
        [p.scale(x, y) for p in self]

    def rot(self, delta: float) -> None:
        """
        in radians
        """
        [p.rot(delta) for p in self]

    def downsample(self, dist: float) -> None:
        [p.downsample(dist) for p in self]

    def simplify(self, e: float) -> None:
        count = self.point_count()

        for p in self:
            p.simplify(e)

        log.info(f"C::simplify from {count} to {self.point_count()} points.")

    def split_by_color(self):
        new_paths = []
        for p in self:
            new_paths.extend(p.split_by_color())

        self.__paths = new_paths

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

    def clip(self, bb: BoundingBox) -> None:
        pp = []
        for p in self.__paths:
            clipped = p.clip(bb)
            if clipped:
                for clip in clipped:
                    pp.append(clip)

        self.__paths = pp

    def clip_shapely(self, bb: BoundingBox) -> None:
        newpaths = []
        for p in self.__paths:
            _p = p.clip_shapely(bb)
            newpaths.extend(_p)
        self.__paths = newpaths

    def calc_travel_distance(self, fac) -> float:
        return reduce(lambda a, b: a + b, [x.distance / fac for x in self.__paths])

    def fit(
            self,
            size=tuple[int, int],
            xy_factor: tuple[float, float] = (1.0, 1.0),
            padding_mm: int = None,
            padding_units: int = None,
            padding_percent: int = None,
            output_bounds: BoundingBox = None,
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
        self.move_to_center(width, height, output_bounds)

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

            self.__paths = [x for x in self.__paths if x.inside(cutoff_bb)]

    def move_to_center(self, width, height, output_bounds=None):
        _bb = self.bb()
        paths_center = _bb.center()

        output_bounds_center = Position(width / 2.0, height / 2.0)

        if output_bounds:
            output_bounds_center = Position.from_tuple(output_bounds.center())

        diff = (
            output_bounds_center.x - paths_center[0],
            output_bounds_center.y - paths_center[1],
        )

        log.info(
            f"{self.__class__.__name__}: fit: translated by {diff[0]:.2f} {diff[1]:.2f}"
        )

        self.translate(diff[0], diff[1])

    def sort_tsp(self, iters=3000, population_size=50, mutation_probability=0.1, plot_preview=False) -> list[int]:
        start_positions = np.array([pa.start_pos().as_tuple() for pa in self])
        end_positions = np.array([pa.end_pos().as_tuple() for pa in self])

        distance_matrix = spatial.distance.cdist(end_positions, start_positions, metric='euclidean')

        def calc_dist(routine):
            num_points, = routine.shape
            return sum(
                [distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])

        ga_tsp = GA_TSP(func=calc_dist, n_dim=len(self.paths), size_pop=population_size, max_iter=iters,
                        prob_mut=mutation_probability)
        best_points, best_distance = ga_tsp.fit()

        if plot_preview:
            fig, ax = plt.subplots(1, 2)
            best_points_ = np.concatenate([best_points, [best_points[0]]])
            best_points_coordinate = start_positions[best_points_, :]
            ax[0].plot(best_points_coordinate[:, 0], best_points_coordinate[:, 1], 'o-r')
            ax[1].plot(ga_tsp.generation_best_Y)
            plt.show()

        final_order = []
        idx = np.where(best_points == 0)[0][0]
        for i in range(idx, len(best_points)):
            final_order.append(best_points[i])
        for i in range(0, idx):
            final_order.append(best_points[i])

        self.paths[:] = [self.paths[i] for i in final_order]

        return final_order

    def reorder_quadrants(self, xq: int, yq: int) -> None:
        if xq < 2 and yq < 2:
            return

        def calc_bb(x: int, y: int) -> BoundingBox:
            big_bb = self.bb()

            new_width = big_bb.w / xq
            new_height = big_bb.h / yq

            _x = x * new_width
            _y = y * new_height

            new_bb = BoundingBox(_x, _y, _x + new_width, _y + new_height)

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

        def _count_inside(_bb: BoundingBox, _pa: Path) -> int:
            c = 0
            for _p in _pa:
                if _p.inside(_bb):
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
