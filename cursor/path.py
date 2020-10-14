from cursor import filter
from cursor import device

import numpy as np
import math
import datetime
import pytz
import random
import hashlib
import wasabi
import copy

log = wasabi.Printer()


class TimedPosition:
    def __init__(self, x=0.0, y=0.0, timestamp=0):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def pos(self):
        return self.x, self.y

    def arr(self):
        return np.array(self.pos(), dtype=float)

    def time(self):
        return self.timestamp

    def copy(self):
        return type(self)(self.x, self.y, self.timestamp)

    def rot(self, delta):
        co = np.cos(delta)
        si = np.sin(delta)
        xx = co * self.x - si * self.y
        yy = si * self.x + co * self.y
        self.x = xx
        self.y = yy

    def translate(self, x, y):
        self.x += x
        self.y += y

    def scale(self, x, y):
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


class BoundingBox:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return f"BB(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def __inside(self, point):
        return self.x < point.x < self.x + self.w and self.y < point.y < self.y + self.h

    def inside(self, data):
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

    def center(self):
        center_x = ((self.w - self.x) / 2) + self.x
        center_y = ((self.h - self.y) / 2) + self.y
        return center_x, center_y


class Path:
    def __init__(self, vertices=None, layer="default"):
        self.layer = layer
        if vertices:
            self.vertices = list(vertices)
        else:
            self.vertices = []

    @property
    def hash(self):
        return hashlib.md5(str(self.vertices).encode("utf-8")).hexdigest()

    def add(self, x, y, timestamp=0):
        self.vertices.append(TimedPosition(x, y, timestamp))

    def clear(self):
        self.vertices.clear()

    def copy(self):
        return type(self)(copy.deepcopy(self.vertices))

    def reverse(self):
        self.vertices.reverse()

    def reversed(self):
        c = copy.deepcopy(self.vertices)
        c.reverse()
        return Path(c, layer=self.layer)

    def start_pos(self):
        if len(self.vertices) == 0:
            raise IndexError
        return self.vertices[0]

    def end_pos(self):
        if len(self.vertices) == 0:
            raise IndexError

        return self.vertices[-1]

    def bb(self):
        minx = min(self.vertices, key=lambda pos: pos.x).x
        miny = min(self.vertices, key=lambda pos: pos.y).y
        maxx = max(self.vertices, key=lambda pos: pos.x).x
        maxy = max(self.vertices, key=lambda pos: pos.y).y
        b = BoundingBox(minx, miny, maxx, maxy)
        return b

    @property
    def distance(self):
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

            d = calculateDistance(current.x, current.y, next.x, next.y,)
            dist += d

        return dist

    def translate(self, x, y):
        for p in self.vertices:
            p.translate(x, y)

    def scale(self, x, y):
        for p in self.vertices:
            p.scale(x, y)

    def morph(self, start, end):
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
            print(w)

        # acos can't properly calculate angle more than 180°.
        # solution taken from here: http://www.gamedev.net/topic/556500-angle-between-vectors/
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

    def intersect(self, newpath):
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
                    lDetDivInv = 1 / ((diffLAx * diffLBy) - (diffLAy * diffLBx))
                    intersectionx = (
                        -((diffLAx * compareB) - (compareA * diffLBx)) * lDetDivInv
                    )
                    intersectiony = (
                        -((diffLAy * compareB) - (compareA * diffLBy)) * lDetDivInv
                    )

                    return True, intersectionx, intersectiony

        return (False,)

    def interp(self, newpath, perc):
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

            path.add(x_interp, y_interp, time_interp)

        return path

    @staticmethod
    def mix(begin, end, perc):
        return ((end - begin) * perc) + begin

    @staticmethod
    def __entropy2(labels, base=None):
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

    def direction_changes(self):
        """
        returns a list of radial direction changes from each point to the next len() = self.__len() - 1
        :return:
        """

        def length(v):
            return np.sqrt(v[0] ** 2 + v[1] ** 2)

        def dot_product(v, w):
            return v[0] * w[0] + v[1] * w[1]

        def determinant(v, w):
            return v[0] * w[1] - v[1] * w[0]

        def inner_angle(v, w):
            dp = dot_product(v, w)
            ll = length(v) * length(w)
            if ll == 0.0:
                return 0.0

            cosx = dp / ll
            rad = np.arccos(cosx)  # in radians
            return rad * 180 / np.pi  # returns degrees

        def angle_clockwise(A, B):
            inner = inner_angle(A, B)
            det = determinant(A, B)
            if (
                det < 0
            ):  # this is a property of the det. If the det < 0 then B is clockwise of A
                return inner
            else:  # if the det > 0 then A is immediately clockwise of B
                return 360 - inner

        angles = []
        idx = 0
        for _ in self.vertices:
            if idx > 0:
                f = self.vertices[idx - 1]
                s = self.vertices[idx]
                angle = angle_clockwise(f.pos(), s.pos())
                # angle = angle_clockwise((1, 1), (1, -1))

                if angle > 180:
                    angle = 360 - angle

                # angles.append(np.deg2rad(angle) % (2 * np.pi))
                angles.append(angle % 360)
            idx += 1

        return angles

    @property
    def shannon_x(self):
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
    def shannon_y(self):
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
    def shannon_direction_changes(self):
        entropy = self.__entropy2(self.direction_changes())
        if entropy is np.nan:
            print("lol")
        return entropy

    def empty(self):
        if len(self.vertices) == 0:
            return True
        return False

    def clean(self):
        new_points = []
        for i in range(1, len(self.vertices)):
            current = self.__getitem__(i - 1)
            next = self.__getitem__(i)
            if current.x == next.x and current.y == next.y:
                if i == len(self.vertices) - 1:
                    new_points.append(current)
                continue

            new_points.append(current)

        self.vertices = new_points

    def __repr__(self):
        rep = f"verts: {len(self.vertices)} shannx: {self.shannon_x} shanny: {self.shannon_y} shannchan: {self.shannon_direction_changes} layer: {self.layer}"
        return rep

    def __len__(self):
        return len(self.vertices)

    def __iter__(self):
        for v in self.vertices:
            yield v

    def __getitem__(self, item):
        return self.vertices[item]


class PathCollection:
    def __init__(self, timestamp=None, name="noname"):
        self.__paths = []
        self.__name = name
        if timestamp:
            self._timestamp = timestamp
        else:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            utc_timestamp = datetime.datetime.timestamp(now)
            self._timestamp = utc_timestamp

    def add(self, path):
        if path.empty():
            return

        self.__paths.append(path)

    def clean(self):
        """
        removes all paths with only one point
        """
        self.__paths = [path for path in self.__paths if len(path) > 1]
        for p in self.__paths:
            p.clean()

    def hash(self):
        return hashlib.md5(str(self.__paths).encode("utf-8")).hexdigest()

    def empty(self):
        if len(self.__paths) == 0:
            return True
        return False

    def get_all(self):
        return self.__paths

    def random(self):
        return self.__getitem__(random.randint(0, self.__len__() - 1))

    def sort(self, pathsorter):
        if isinstance(pathsorter, filter.Sorter):
            pathsorter.sort(self.__paths)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def sorted(self, pathsorter):
        if isinstance(pathsorter, filter.Sorter):
            return pathsorter.sorted(self.__paths)
        else:
            raise Exception(f"Cant sort with a class of type {type(pathsorter)}")

    def filter(self, pathfilter):
        if isinstance(pathfilter, filter.Filter):
            pathfilter.filter(self.__paths)
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def filtered(self, pathfilter):
        if isinstance(pathfilter, filter.Filter):

            pc = PathCollection()
            pc.__paths = pathfilter.filtered(self.__paths)
            return pc
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def __len__(self):
        return len(self.__paths)

    def __add__(self, other):
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

    def __repr__(self):
        return f"PathCollection({self.__name}) -> ({self.__paths})"

    def __eq__(self, other):
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

    def __getitem__(self, item):
        if len(self.__paths) < item + 1:
            raise IndexError(f"Index too high. Maximum is {len(self.__paths)}")
        return self.__paths[item]

    def timestamp(self):
        return self._timestamp

    def layer_names(self):
        layers = []
        for p in self.__paths:
            if p.layer not in layers:
                layers.append(p.layer)

        return layers

    def get_layers(self):
        layers = {}
        for layer in self.layer_names():
            layers[layer] = []

        for p in self.__paths:
            layers[p.layer].append(p)

        layered_pcs = {}
        for key in layers:
            pc = PathCollection()
            pc.__paths.extend(layers[key])
            layered_pcs[key] = pc

        return layered_pcs

    def bb(self):
        mi = self.min()
        ma = self.max()
        bb = BoundingBox(mi[0], mi[1], ma[0], ma[1])
        if bb.x is np.nan or bb.y is np.nan or bb.w is np.nan or bb.h is np.nan:
            print("f8co")
        return bb

    def min(self):
        all_chained = [point for path in self.__paths for point in path]
        minx = min(all_chained, key=lambda pos: pos.x).x
        miny = min(all_chained, key=lambda pos: pos.y).y
        return minx, miny

    def max(self):
        all_chained = [point for path in self.__paths for point in path]
        maxx = max(all_chained, key=lambda pos: pos.x).x
        maxy = max(all_chained, key=lambda pos: pos.y).y
        return maxx, maxy

    def translate(self, x, y):
        for p in self.__paths:
            p.translate(x, y)

    def scale(self, x, y):
        for p in self.__paths:
            p.scale(x, y)

    def fit(
        self,
        size,
        machine=device.DrawingMachine(),
        padding_mm=None,
        padding_units=None,
        padding_percent=None,
        center_point=None,
    ):
        # move into positive area
        _bb = self.bb()
        if _bb.x < 0:
            log.good(f"{__class__.__name__}: fit: translate by {_bb.x} {0.0}")
            self.translate(abs(_bb.x), 0.0)
        else:
            log.good(f"{__class__.__name__}: fit: translate by {-abs(_bb.x)} {0.0}")
            self.translate(-abs(_bb.x), 0.0)

        if _bb.y < 0:
            log.good(f"{__class__.__name__}: fit: translate by {0.0} {abs(_bb.y)}")
            self.translate(0.0, abs(_bb.y))
        else:
            log.good(f"{__class__.__name__}: fit: translate by {0.0} {-abs(_bb.y)}")
            self.translate(0.0, -abs(_bb.y))
        _bb = self.bb()
        width = size[0]
        height = size[1]

        padding_x = 0
        padding_y = 0

        if padding_mm is not None and padding_units is None and padding_percent is None:
            padding_x = padding_mm * machine.Paper.X_FACTOR
            padding_y = padding_mm * machine.Paper.Y_FACTOR

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

        y1 = height - padding_y * 2.0
        y2 = _bb.h - _bb.y

        xfac = x1 / x2
        yfac = y1 / y2

        log.good(f"{__class__.__name__}: fit: scaled by {xfac} {yfac}")

        self.scale(xfac, yfac)

        print(self.bb())

        # centering

        _bb = self.bb()
        center = _bb.center()
        if center_point is None:
            center_dims = width / 2.0, height / 2.0
        else:
            center_dims = center_point
        diff = center_dims[0] - center[0], center_dims[1] - center[1]

        log.good(f"{__class__.__name__}: fit: translated by {diff[0]} {diff[1]}")

        self.translate(diff[0], diff[1])

        print(self.bb())
