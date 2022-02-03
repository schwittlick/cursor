from cursor import filter as cursor_filter

import numpy as np
import math
import datetime
import pytz
import random
import hashlib
import wasabi
import copy
import typing
import operator
import time
from scipy import spatial


log = wasabi.Printer()


class TimedPosition:
    def __init__(self, x: float = 0.0, y: float = 0.0, timestamp: int = 0):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def pos(self) -> tuple[float, float]:
        return self.x, self.y

    def arr(self) -> np.array:
        return np.array(self.pos(), dtype=float)

    def time(self) -> int:
        return self.timestamp

    def copy(self) -> "TimedPosition":
        return type(self)(
            copy.deepcopy(self.x), copy.deepcopy(self.y), copy.deepcopy(self.timestamp)
        )

    def distance(self, t: "TimedPosition"):
        return np.linalg.norm(self.arr() - t.arr())

    def rot(self, delta: float) -> None:
        co = np.cos(delta)
        si = np.sin(delta)
        xx = co * self.x - si * self.y
        yy = si * self.x + co * self.y
        self.x = xx
        self.y = yy

    def translate(self, x: float, y: float) -> None:
        self.x += x
        self.y += y

    def scale(self, x: float, y: float) -> None:
        self.x *= x
        self.y *= y

    def __eq__(self, o):
        """
        compare equality by comparing all fields
        """
        if not isinstance(o, TimedPosition):
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

    def __mul__(self, other: "TimedPosition"):
        return self.arr() * other.arr()


class BoundingBox:
    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self) -> str:
        return f"BB(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def __inside(self, point: "TimedPosition") -> bool:
        return (
            self.x <= point.x <= self.x + self.w
            and self.y <= point.y <= self.y + self.h
        )

    def inside(
        self, data: typing.Union["TimedPosition", "Path", "PathCollection"]
    ) -> bool:
        if isinstance(data, TimedPosition):
            return self.__inside(data)
        if isinstance(data, Path):
            for p in data:
                if not self.__inside(p):
                    return False
            return True
        if isinstance(data, PathCollection):
            for path in data:
                for p in path:
                    if not self.__inside(p):
                        return False
            return True

    def mostly_inside(self, data: "Path") -> bool:
        points_inside = 0
        points_outside = 0
        if isinstance(data, Path):
            for p in data:
                if not self.__inside(p):
                    points_outside += 1
                else:
                    points_inside += 1
            return points_inside > points_outside

    def center(self) -> typing.Tuple[float, float]:
        center_x = ((self.w) / 2.0) + self.x
        center_y = ((self.h) / 2.0) + self.y
        return center_x, center_y


class Spiral:
    def __init__(self):
        self.theta = 0
        self.theta_incr = 0.02
        self.max_theta = 255
        self.r = 50
        self.xoffset = 0
        self.xoffset_incr = 0.55
        self.maxx = 1888

    def reset(self):
        self.theta = 0
        self.xoffset = 0

    def custom(self, pp):
        while self.theta < self.max_theta:
            y = self.r * math.cos(self.theta) * 2
            x = self.r * math.sin(self.theta) + self.xoffset
            pp.add(x, y, 0)
            self.theta += self.theta_incr
            self.xoffset += self.xoffset_incr
            if x >= self.maxx:
                break

        return pp

    def get_plain(self, pp):
        self.theta = 0
        self.theta_incr = 0.02
        self.max_theta = 255
        self.r = 50
        self.xoffset = 0
        self.xoffset_incr = 0.15
        self.maxx = 1888

        return self.custom(pp)


class Path:
    def __init__(
        self,
        vertices: typing.Optional[list] = None,
        layer: typing.Optional[str] = None,
        line_type: typing.Optional[int] = None,
        pen_velocity: typing.Optional[int] = None,
        pen_force: typing.Optional[int] = None,
        pen_select: typing.Optional[int] = None,
        is_polygon: typing.Optional[bool] = None
    ):
        self._layer = layer
        self._line_type = line_type
        self._pen_velocity = pen_velocity
        self._pen_force = pen_force
        self._pen_select = pen_select
        self._is_polygon = is_polygon
        if vertices:
            self.vertices = list(vertices)
        else:
            self.vertices = []

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self.vertices).encode("utf-8")).hexdigest()

    @property
    def line_type(self):
        """
        only linetype of 1 and above allowed
        all other linetypes don't render well
        """
        if self._line_type is None:
            return 1
        return max(self._line_type, 1)

    @line_type.setter
    def line_type(self, line_type):
        if line_type <= 0:
            self._line_type = 1
        self._line_type = line_type

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer):
        self._layer = layer

    @property
    def pen_force(self):
        return self._pen_force

    @pen_force.setter
    def pen_force(self, pen_force):
        self._pen_force = pen_force

    @property
    def pen_select(self):
        return self._pen_select

    @pen_select.setter
    def pen_select(self, pen_select):
        self._pen_select = pen_select

    @property
    def velocity(self):
        return self._pen_velocity

    @velocity.setter
    def velocity(self, pen_velocity):
        self._pen_velocity = pen_velocity

    @property
    def is_polygon(self):
        return self._is_polygon

    @is_polygon.setter
    def is_polygon(self, is_polygon):
        self._is_polygon = is_polygon

    def add(self, x: float, y: float, timestamp: int = 0) -> None:
        self.vertices.append(TimedPosition(x, y, timestamp))

    def arr(self):
        data = np.random.randint(0, 1000, size=(len(self), 2))

        idx = 0
        for p in self.vertices:
            data[idx] = p.arr()
            idx += 1

        return data

    def clear(self) -> None:
        self.vertices.clear()

    def copy(self) -> "Path":
        return type(self)(copy.deepcopy(self.vertices))

    def reverse(self) -> None:
        self.vertices.reverse()

    def reversed(self) -> "Path":
        c = copy.deepcopy(self.vertices)
        c.reverse()
        return Path(
            c, layer=self.layer, line_type=self.line_type, pen_velocity=self.velocity
        )

    def start_pos(self) -> "TimedPosition":
        if len(self.vertices) == 0:
            raise IndexError
        return self.vertices[0]

    def end_pos(self) -> "TimedPosition":
        if len(self.vertices) == 0:
            raise IndexError

        return self.vertices[-1]

    def bb(self) -> BoundingBox:
        minx = min(self.vertices, key=lambda pos: pos.x).x
        miny = min(self.vertices, key=lambda pos: pos.y).y
        maxx = max(self.vertices, key=lambda pos: pos.x).x
        maxy = max(self.vertices, key=lambda pos: pos.y).y
        b = BoundingBox(minx, miny, maxx, maxy)
        return b

    @property
    def distance(self) -> float:
        """
        Calculates the summed distance between all points in sequence
        Also known as "travel distance"
        """
        dist = 0

        def calculateDistance(x1, y1, x2, y2):
            dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            return dist

        for i in range(self.__len__() - 1):
            current = self.__getitem__(i)
            next = self.__getitem__(i + 1)

            d = calculateDistance(current.x, current.y, next.x, next.y)
            dist += d

        return dist

    def translate(self, x: float, y: float) -> None:
        for p in self.vertices:
            p.translate(x, y)

    def scale(self, x: float, y: float) -> None:
        for p in self.vertices:
            p.scale(x, y)

    def morph(
        self,
        start: typing.Union["TimedPosition", typing.Tuple[float, float]],
        end: typing.Union["TimedPosition", typing.Tuple[float, float]],
    ) -> "Path":
        if isinstance(start, TimedPosition) and isinstance(end, TimedPosition):
            start = (start.x, start.y)
            end = (end.x, end.y)

        path = Path()
        end_np = self.end_pos().arr()
        start_np = self.start_pos().arr()
        new_end_np = np.array(end, dtype=float)
        new_start_np = np.array(start, dtype=float)

        for point in self.vertices:
            nparr = point.arr()

            dir_old = np.subtract(end_np, start_np)
            dir_new = np.subtract(new_end_np, new_start_np)
            mag_diff = np.linalg.norm(dir_new) / np.linalg.norm(dir_old)
            if mag_diff is np.nan:
                mag_diff = 0.0
            if math.isinf(mag_diff):
                mag_diff = 1.0
            nparr = nparr * mag_diff
            path.add(nparr[0], nparr[1], point.timestamp)

        current_end = path.end_pos().arr()
        current_start = path.start_pos().arr()
        current_start_to_end = np.subtract(current_end, current_start)

        new_start_to_end = np.subtract(new_end_np, new_start_np)

        current_start_to_end = current_start_to_end / np.linalg.norm(
            current_start_to_end
        )
        new_start_to_end = new_start_to_end / np.linalg.norm(new_start_to_end)

        try:
            angle = np.arccos(
                np.clip(
                    np.dot(current_start_to_end, new_start_to_end), -math.pi, math.pi
                )
            )
        except RuntimeWarning as w:
            log.fail(w)

        # acos can't properly calculate angle more than 180°.
        # solution taken from here:
        # http://www.gamedev.net/topic/556500-angle-between-vectors/
        if (
            current_start_to_end[0] * new_start_to_end[1]
            < current_start_to_end[1] * new_start_to_end[0]
        ):
            angle = 2 * math.pi - angle

        for p in path.vertices:
            p.rot(angle)

        translation = np.subtract(new_start_np, path.start_pos().arr())
        for p in path.vertices:
            p.translate(translation[0], translation[1])

        return path

    def intersect(self, newpath: "Path") -> typing.Tuple[bool, float, float]:
        for p1 in range(len(newpath) - 1):
            for p2 in range(len(self) - 1):
                line1Start = newpath[p1]
                line1End = newpath[p1 + 1]
                line2Start = self[p2]
                line2End = self[p2 + 1]

                diffLAx = line1End.x - line1Start.x
                diffLAy = line1End.y - line1Start.y
                diffLBx = line2End.x - line2Start.x
                diffLBy = line2End.y - line2Start.y
                compareA = diffLAx * line1Start.y - diffLAy * line1Start.x
                compareB = diffLBx * line2Start.y - diffLBy * line2Start.x
                if ((diffLAx * line2Start.y - diffLAy * line2Start.x) < compareA) ^ (
                    (diffLAx * line2End.y - diffLAy * line2End.x) < compareA
                ) and ((diffLBx * line1Start.y - diffLBy * line1Start.x) < compareB) ^ (
                    (diffLBx * line1End.y - diffLBy * line1End.x) < compareB
                ):
                    ok = ((diffLAx * diffLBy) - (diffLAy * diffLBx))
                    if ok == 0:
                        ok = 0.01
                    lDetDivInv = 1 / ok
                    intersectionx = (
                        -((diffLAx * compareB) - (compareA * diffLBx)) * lDetDivInv
                    )
                    intersectiony = (
                        -((diffLAy * compareB) - (compareA * diffLBy)) * lDetDivInv
                    )

                    return True, intersectionx, intersectiony

        return False, 0.0, 0.0

    def interp(self, newpath: "Path", perc: float) -> "Path":
        path = Path()

        maxpoint = max(len(newpath), len(self))

        for i in range(maxpoint):
            idxthis = int((float(i) / maxpoint) * len(self))
            idxnew = int((float(i) / maxpoint) * len(newpath))

            pthis = self[idxthis]
            pnew = newpath[idxnew]
            x_interp = self.mix(pthis.x, pnew.x, perc)
            y_interp = self.mix(pthis.y, pnew.y, perc)
            time_interp = self.mix(pthis.timestamp, pnew.timestamp, perc)

            path.add(x_interp, y_interp, int(time_interp))

        return path

    @staticmethod
    def mix(begin: float, end: float, perc: float):
        return ((end - begin) * perc) + begin

    @staticmethod
    def __entropy2(labels: list, base=None) -> float:
        from math import log, e

        """ Computes entropy of label distribution. """

        n_labels = len(labels)

        if n_labels <= 1:
            return 0

        value, counts = np.unique(labels, return_counts=True)
        probs = counts / n_labels
        n_classes = np.count_nonzero(probs)

        if n_classes <= 1:
            return 0

        ent = 0.0

        # Compute entropy
        base = e if base is None else base
        for i in probs:
            ent -= i * log(i, base)

        return ent

    def direction_changes_pos_neg(self) -> typing.List[float]:
        """
        returns a list of radial direction changes from each point
        to the next len() = self.__len() - 1
        :return:
        """

        angles = []
        idx = 0
        prev = 0
        for _ in self.vertices:
            if idx > 0:
                f = self.vertices[idx - 1]
                s = self.vertices[idx]

                ang = math.atan2(s.y - f.y, s.x - f.x)
                ang = math.degrees(ang)

                angles.append(ang - prev)
                prev = ang
            idx += 1

        return angles

    @staticmethod
    def length(v):
        return np.sqrt(v[0] ** 2 + v[1] ** 2)

    @staticmethod
    def dot_product(v, w):
        return v[0] * w[0] + v[1] * w[1]

    @staticmethod
    def determinant(v, w):
        return v[0] * w[1] - v[1] * w[0]

    def inner_angle(self, v, w):
        dp = self.dot_product(v, w)
        ll = self.length(v) * self.length(w)
        if ll == 0.0:
            return 0.0

        cosx = dp / ll

        if cosx < -1.0:
            cosx = -1.0
        if cosx > 1.0:
            cosx = 1.0

        rad = np.arccos(cosx)  # in radians
        return rad * 180 / np.pi  # returns degrees

    def angle_clockwise(self, A, B):
        inner = self.inner_angle(A, B)
        det = self.determinant(A, B)
        if det < 0:
            # this is a property of the det. If the det < 0 then B is clockwise of A
            return inner
        else:  # if the det > 0 then A is immediately clockwise of B
            return 360 - inner

    def direction_changes(self) -> typing.List[float]:
        """
        returns a list of radial direction changes from each point
        to the next len() = self.__len() - 1
        :return:
        """
        angles = []
        idx = 0
        for _ in self.vertices:
            if idx > 0:
                f = self.vertices[idx - 1]
                s = self.vertices[idx]
                angle = self.angle_clockwise(f.pos(), s.pos())
                # angle = angle_clockwise((1, 1), (1, -1))

                if angle > 180:
                    angle = 360 - angle

                # angles.append(np.deg2rad(angle) % (2 * np.pi))
                angles.append(angle % 360)
            idx += 1

        return angles

    @property
    def shannon_x(self) -> float:
        distances = []

        first = True
        prevx = None
        for v in self.vertices:
            if first:
                prevx = v.x
                first = False
                continue

            dist = v.x - prevx
            distances.append(dist)

            prevx = v.x

        entropy = self.__entropy2(distances)
        return entropy

    @property
    def shannon_y(self) -> float:
        distances = []

        first = True
        prevy = None
        for v in self.vertices:
            if first:
                prevy = v.y
                first = False
                continue

            dist = v.y - prevy
            distances.append(dist)

            prevy = v.y

        entropy = self.__entropy2(distances)
        return entropy

    @property
    def shannon_direction_changes(self) -> float:
        entropy = self.__entropy2(self.direction_changes())
        if entropy is np.nan:
            log.fail("LOL")
        return entropy

    def empty(self) -> bool:
        return len(self.vertices) == 0

    def clean(self) -> None:
        """
        removes consecutive duplicates
        """
        prev = TimedPosition()
        self.vertices = [prev := v for v in self.vertices if prev != v]

    def limit(self) -> None:
        """
        removes points larger than 1.0
        """
        self.vertices = [prev := v for v in self.vertices if v.x < 1.0 and v.y < 1.0]

    def similarity(self, _path: "Path") -> float:
        """
        this does not really work..

        most similarities are > 0.7, even for severely un-similar
        paths. what might help is to normalize them (and their BB)
        into the space around the (0, 0) origin. but i'm not really
        sure. similarity between a list of coordinates doesn't seem
        to be a trivial thing. especially when you want some meaningful
        results. to be continued. :)
        """
        if len(self) < len(_path):
            diff = len(_path) - len(self)
            _t = self.vertices.copy()
            for i in range(diff):
                _t.append(self.end_pos())
            result = 1 - spatial.distance.cosine(_t, _path.vertices)
            return result[1]

        if len(_path) < len(self):
            diff = len(self) - len(_path)
            _t = _path.vertices.copy()
            for i in range(diff):
                _t.append(_path.end_pos())
            result = 1 - spatial.distance.cosine(self.vertices, _t)
            return result[1]

        result = 1 - spatial.distance.cosine(self.vertices, _path.vertices)
        return result[1]

    def centeroid(self):
        arr = self.arr()
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x / length, sum_y / length

    def __repr__(self):
        rep = (
            f"verts: {len(self.vertices)} shannx: {self.shannon_x} shanny: {self.shannon_y} "
            f"shannchan: {self.shannon_direction_changes} layer: {self.layer} "
            f"type: {self.line_type} velocity: {self.velocity}"
        )
        return rep

    def __len__(self) -> int:
        return len(self.vertices)

    def __iter__(self):
        for v in self.vertices:
            yield v

    def __getitem__(self, item):
        return self.vertices[item].copy()


class PathCollection:
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

    def add(self, path: Path) -> None:
        if path.empty():
            return
        self.__paths.append(path)

    def extend(self, pc: "PathCollection") -> None:
        new_paths = self.__paths + pc.get_all()
        self.__paths = new_paths

    def clean(self) -> None:
        """
        removes all paths with only one point
        """
        for p in self.__paths:
            p.clean()

        self.__paths = [path for path in self.__paths if len(path) > 2]

    def limit(self) -> None:
        for p in self.__paths:
            p.limit()

    def hash(self) -> str:
        return hashlib.md5(str(self.__paths).encode("utf-8")).hexdigest()

    def empty(self) -> bool:
        if len(self.__paths) == 0:
            return True
        return False

    def copy(self) -> "PathCollection":
        p = PathCollection()
        p.__paths.extend(copy.deepcopy(self.__paths))
        return p

    def get_all(self) -> typing.List[Path]:
        return self.__paths

    def random(self) -> Path:
        return self.__getitem__(random.randint(0, self.__len__() - 1))

    def sort(self, pathsorter: "cursor_filter.Sorter") -> None:
        if isinstance(pathsorter, cursor_filter.Sorter):
            pathsorter.sort(self.__paths)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def sorted(self, pathsorter: "cursor_filter.Sorter") -> typing.List[Path]:
        if isinstance(pathsorter, cursor_filter.Sorter):
            return pathsorter.sorted(self.__paths)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def filter(self, pathfilter: "cursor_filter.Filter") -> None:
        if isinstance(pathfilter, cursor_filter.Filter):
            pathfilter.filter(self.__paths)
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def filtered(self, pathfilter: "cursor_filter.Filter") -> "PathCollection":
        if isinstance(pathfilter, cursor_filter.Filter):

            pc = PathCollection()
            pc.__paths = pathfilter.filtered(self.__paths)
            return pc
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def __len__(self) -> int:
        return len(self.__paths)

    def __add__(self, other: typing.Union[list, "PathCollection"]) -> "PathCollection":
        if isinstance(other, PathCollection):
            new_paths = self.__paths + other.get_all()
            p = PathCollection()
            p.__paths.extend(new_paths)
            return p
        if isinstance(other, list):
            new_paths = self.__paths + other
            p = PathCollection()
            p.__paths.extend(new_paths)
            return p
        else:
            raise Exception(
                "You can only add another PathCollection or a list of paths"
            )

    def __repr__(self) -> str:
        return f"PathCollection({self.__name}) -> ({self.__paths})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, PathCollection):
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
    ) -> typing.Union["PathCollection", Path]:
        if isinstance(item, slice):
            start, stop, step = item.indices(len(self))
            _pc = PathCollection()
            _pc.__paths = [self[i] for i in range(start, stop, step)]
            return _pc

        if len(self.__paths) < item + 1:
            raise IndexError(f"Index too high. Maximum is {len(self.__paths)}")

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
            pc = PathCollection()
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
            pc = PathCollection()
            pc.__paths.extend(layers[key])
            layered_pcs[key] = pc

        return layered_pcs

    def bb(self) -> BoundingBox:
        mi = self.min()
        ma = self.max()
        bb = BoundingBox(mi[0], mi[1], ma[0] - mi[0], ma[1] - mi[1])
        if bb.x is np.nan or bb.y is np.nan or bb.w is np.nan or bb.h is np.nan:
            log.fail("SHIT")
        return bb

    def min(self) -> typing.Tuple[float, float]:
        all_chained = [point for path in self.__paths for point in path]
        minx = min(all_chained, key=lambda pos: pos.x).x
        miny = min(all_chained, key=lambda pos: pos.y).y
        return minx, miny

    def max(self) -> typing.Tuple[float, float]:
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

    def log(self, str) -> None:
        log.good(f"{self.__class__.__name__}: {str}")

    def fit(
        self,
        size=tuple[int, int],
        xy_factor: tuple[float, float] = (2.85714, 2.90572),
        padding_mm: int = None,
        padding_units: int = None,
        padding_percent: int = None,
        output_bounds: tuple[float, float, float, float] = None,
        cutoff_mm=None,
    ) -> None:
        # move into positive area
        _bb = self.bb()
        if _bb.x < 0:
            log.info("fit: translate by {_bb.x:.2f} {0.0}")
            self.translate(abs(_bb.x), 0.0)
        else:
            log.info("fit: translate by {-abs(_bb.x):.2f} {0.0}")
            self.translate(-abs(_bb.x), 0.0)

        if _bb.y < 0:
            log.info("fit: translate by {0.0} {abs(_bb.y):.2f}")
            self.translate(0.0, abs(_bb.y))
        else:
            log.info("fit: translate by {0.0} {-abs(_bb.y):.2f}")
            self.translate(0.0, -abs(_bb.y))

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
        x1 = width - padding_x * 2.0
        x2 = _bb.w - _bb.x
        if x2 == 0.0:
            x2 = 1

        y1 = height - padding_y * 2.0
        y2 = _bb.h - _bb.y
        if y2 == 0.0:
            y2 = 1

        xfac = x1 / x2
        yfac = y1 / y2

        log.info(f"{self.__class__.__name__}: fit: scaled by {xfac:.2f} {yfac:.2f}")

        self.scale(xfac, yfac)

        # centering
        _bb = self.bb()
        paths_center = _bb.center()

        output_bounds_center = width / 2.0, height / 2.0

        if output_bounds:
            w = np.linalg.norm(output_bounds[1] - output_bounds[0])
            h = np.linalg.norm(output_bounds[3] - output_bounds[2])
            output_bounds_center = BoundingBox(
                output_bounds[0], output_bounds[2], w, h,
            ).center()

        diff = (
            output_bounds_center[0] - paths_center[0],
            output_bounds_center[1] - paths_center[1],
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
            cutoff_bb.w += cuttoff_margin_diff_x
            cutoff_bb.y -= cuttoff_margin_diff_y
            cutoff_bb.h += cuttoff_margin_diff_y

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

        def calc_bb(x: int, y: int) -> BoundingBox:
            big_bb = self.bb()

            new_width = big_bb.w / xq
            new_height = big_bb.h / yq

            _x = x * new_width
            _y = y * new_height

            new_bb = BoundingBox(_x, _y, new_width, new_height)

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
