import numpy as np
import math
import datetime
import pytz
import json
import pyautogui


class MyJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PathCollection):
            return {'paths': o.get_all(), 'resolution': {'w': o.resolution.width, 'h': o.resolution.height}}

        if isinstance(o, Path):
            return o.vertices

        if isinstance(o, TimedPosition):
            return {'x': round(o.x, 4), 'y': round(o.y, 4), 'ts': round(o.timestamp, 2)}


class MyJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if 'x' in dct and 'y' in dct and 'ts' in dct:
            p = TimedPosition(dct['x'], dct['y'], dct['ts'])
            return p
        if 'w' in dct and 'h' in dct:
            s = pyautogui.Size(dct['w'], dct['h'])
            return s
        if 'paths' in dct and 'resolution' in dct:
            res = dct['resolution']
            pc = PathCollection(res)
            for p in dct['paths']:
                pc.add(Path(p), res)
            return pc
        return dct


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
        return F"({self.x:.3f}, {self.y:.3f}, {self.timestamp:.3f})"


class Path:
    def __init__(self, vertices=None):
        if vertices:
            self.vertices = list(vertices)
        else:
            self.vertices = []

    def add(self, x, y, timestamp):
        self.vertices.append(TimedPosition(x, y, timestamp))

    def clear(self):
        self.vertices.clear()

    def copy(self):
        return type(self)(self.vertices.copy())

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
            nparr = nparr * mag_diff
            path.add(nparr[0], nparr[1], point.timestamp)

        current_end = path.end_pos().arr()
        current_start = path.start_pos().arr()
        current_start_to_end = np.subtract(current_end, current_start)

        new_start_to_end = np.subtract(new_end_np, new_start_np)

        current_start_to_end = current_start_to_end / np.linalg.norm(current_start_to_end)
        new_start_to_end = new_start_to_end / np.linalg.norm(new_start_to_end)

        angle = np.arccos(np.clip(np.dot(current_start_to_end, new_start_to_end), -math.pi, math.pi))

        for p in path.vertices:
            p.rot(angle)

        translation = np.subtract(new_start_np, path.start_pos().arr())
        for p in path.vertices:
            p.translate(translation[0], translation[1])

        return path

    def empty(self):
        if len(self.vertices) == 0:
            return True
        return False

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
        if resolution.width != self.resolution.width or resolution.height != self.resolution.height:
            raise Exception('New resolution is different to current. This should be handled somehow ..')

        if path.empty():
            return

        self.__paths.append(path)

    def empty(self):
        if len(self.__paths) == 0:
            return True
        return False

    def get_all(self):
        return self.__paths

    def __len__(self):
        return len(self.__paths)

    def __add__(self, other):
        if isinstance(other, PathCollection):
            if other.resolution.width != self.resolution.width or other.resolution.height != self.resolution.height:
                raise Exception('New resolution is different to current. This should be handled somehow ..')

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
            raise Exception('You can only add another PathCollection or a list of paths')

    def __repr__(self):
        return f"PathCollection({self.resolution}, {self.__paths})"

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
            raise IndexError('Index too high')
        return self.__paths[item]

    def timestamp(self):
        return self._timestamp

    def bb(self):
        mi = self.min()
        ma = self.max()
        return mi[0], mi[1], ma[0], ma[1]

    def min(self):
        all_chained = [point for path in self.__paths for point in path]
        minx = min(all_chained, key = lambda pos: pos.x).x
        miny = min(all_chained, key = lambda pos: pos.y).y
        return minx, miny

    def max(self):
        all_chained = [point for path in self.__paths for point in path]
        maxx = max(all_chained, key=lambda pos: pos.x).x
        maxy = max(all_chained, key=lambda pos: pos.y).y
        return maxx, maxy