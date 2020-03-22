from cursor import filter

import numpy as np
import math
import datetime
import pytz
import json
import base64
import zlib
import pyautogui
import random
import hashlib


class MyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PathCollection):
            return {
                "paths": o.get_all(),
                "resolution": {"w": o.resolution.width, "h": o.resolution.height},
                "timestamp": o.timestamp(),
            }

        if isinstance(o, Path):
            return o.vertices

        if isinstance(o, TimedPosition):
            return {"x": round(o.x, 4), "y": round(o.y, 4), "ts": round(o.timestamp, 2)}


class MyJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "x" in dct and "y" in dct and "ts" in dct:
            p = TimedPosition(dct["x"], dct["y"], dct["ts"])
            return p
        if "w" in dct and "h" in dct:
            s = pyautogui.Size(dct["w"], dct["h"])
            return s
        if "paths" in dct and "resolution" in dct and "timestamp" in dct:
            res = dct["resolution"]
            ts = dct["timestamp"]
            pc = PathCollection(res, ts)
            for p in dct["paths"]:
                pc.add(Path(p), res)
            return pc
        return dct


class JsonCompressor:
    ZIPJSON_KEY = "base64(zip(o))"

    def json_zip(self, j):

        j = {
            self.ZIPJSON_KEY: base64.b64encode(
                zlib.compress(json.dumps(j, cls=MyJsonEncoder).encode("utf-8"))
            ).decode("ascii")
        }

        return j

    def json_unzip(self, j, insist=True):
        try:
            assert j[self.ZIPJSON_KEY]
            assert set(j.keys()) == {self.ZIPJSON_KEY}
        except:
            if insist:
                raise RuntimeError(
                    "JSON not in the expected format {"
                    + str(self.ZIPJSON_KEY)
                    + ": zipstring}"
                )
            else:
                return j

        try:
            j = zlib.decompress(base64.b64decode(j[self.ZIPJSON_KEY]))
        except:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            j = json.loads(j, cls=MyJsonDecoder)
        except:
            raise RuntimeError("Could interpret the unzipped contents")

        return j


class Paper:
    X_FACTOR = 2.91666
    Y_FACTOR = 2.83333

    CUSTOM_36_48 = (360 * X_FACTOR, 480 * Y_FACTOR)
    CUSTOM_48_36 = (480 * X_FACTOR, 360 * Y_FACTOR)
    DIN_A1_LANDSCAPE = (841 * X_FACTOR, 594 * Y_FACTOR)
    DIN_A0_LANDSCAPE = (1189 * X_FACTOR, 841 * Y_FACTOR)

    @staticmethod
    def custom_36_48_portrait():
        return Paper.CUSTOM_36_48

    @staticmethod
    def custom_36_48_landscape():
        return Paper.CUSTOM_48_36

    @staticmethod
    def a1_landscape():
        return Paper.DIN_A1_LANDSCAPE

    @staticmethod
    def a0_landscape():
        return Paper.DIN_A0_LANDSCAPE


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
        return self.x + self.w / 2, self.y + self.h / 2


class Path:
    def __init__(self, vertices=None):
        if vertices:
            self.vertices = list(vertices)
        else:
            self.vertices = []

    def hash(self):
        return hashlib.md5(str(self.vertices).encode("utf-8")).hexdigest()

    def add(self, x, y, timestamp):
        self.vertices.append(TimedPosition(x, y, timestamp))

    def clear(self):
        self.vertices.clear()

    def copy(self):
        return type(self)(self.vertices.copy())

    def reverse(self):
        self.vertices.reverse()

    def reversed(self):
        c = self.vertices.copy()
        c.reverse()
        return Path(c)

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

        return minx, miny, maxx, maxy

    def distance(self, res):
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

            d = calculateDistance(
                current.x * res.width,
                current.y * res.height,
                next.x * res.width,
                next.y * res.height,
            )
            dist += d

        return dist

    def translate(self, x, y):
        for p in self.vertices:
            p.translate(x, y)

    def scale(self, x, y):
        for p in self.vertices:
            p.scale(x, y)

    def morph(self, start, end):
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

        angle = np.arccos(
            np.clip(np.dot(current_start_to_end, new_start_to_end), -math.pi, math.pi)
        )

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
        return str(self.vertices)

    def __len__(self):
        return len(self.vertices)

    def __iter__(self):
        for v in self.vertices:
            yield v

    def __getitem__(self, item):
        return self.vertices[item]


class PathCollection:
    def __init__(self, resolution, timestamp=None):
        self.__paths = []
        if timestamp:
            self._timestamp = timestamp
        else:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            utc_timestamp = datetime.datetime.timestamp(now)
            self._timestamp = utc_timestamp
        self.resolution = resolution

    def add(self, path, resolution):
        if (
            resolution.width != self.resolution.width
            or resolution.height != self.resolution.height
        ):
            raise Exception(
                "New resolution is different to current. This should be handled somehow .."
            )

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

    def filter(self, pathfilter):
        if isinstance(pathfilter, filter.Filter):
            pathfilter.filter(self.__paths)
        else:
            raise Exception(f"Cant filter with a class of type {type(pathfilter)}")

    def __len__(self):
        return len(self.__paths)

    def __add__(self, other):
        if isinstance(other, PathCollection):
            if (
                other.resolution.width != self.resolution.width
                or other.resolution.height != self.resolution.height
            ):
                raise Exception(
                    "New resolution is different to current. This should be handled somehow .."
                )

            new_paths = self.__paths + other.get_all()
            p = PathCollection(self.resolution)
            p.__paths.extend(new_paths)
            return p
        if isinstance(other, list):
            new_paths = self.__paths + other
            p = PathCollection(self.resolution)
            p.__paths.extend(new_paths)
            return p
        else:
            raise Exception(
                "You can only add another PathCollection or a list of paths"
            )

    def __repr__(self):
        return f"PathCollection({self.resolution}, {self.__paths})"

    def __eq__(self, other):
        if not isinstance(other, PathCollection):
            return NotImplemented

        if len(self) != len(other):
            return False

        if self.timestamp() != other.timestamp():
            return False

        if (
            other.resolution.width != self.resolution.width
            or other.resolution.height != self.resolution.height
        ):
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

    def bb(self):
        mi = self.min()
        ma = self.max()
        bb = BoundingBox(mi[0], mi[1], ma[0] - mi[0], ma[1] - mi[1])
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

    def fit(self, size, padding_mm):
        width = size[0]
        height = size[1]
        padding_x = padding_mm * Paper.X_FACTOR
        padding_y = padding_mm * Paper.Y_FACTOR

        # scaling
        xfac = (width - padding_x * 2) / self.bb().w
        yfac = (height - padding_y * 2) / self.bb().h
        self.scale(xfac, yfac)

        # centering
        center = self.bb().center()
        center_dims = width / 2, height / 2
        diff = center_dims[0] - center[0], center_dims[1] - center[1]

        self.translate(diff[0], diff[1])
