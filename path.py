import numpy as np
import math

class TimedPosition(object):
    def __init__(self, x, y, timestamp):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def pos(self):
        return self.x, self.y

    def time(self):
        return self.timestamp

    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.timestamp})"


class Path(object):
    def __init__(self):
        self.vertices = []

    def add(self, x, y, timestamp):
        self.vertices.append(TimedPosition(x, y, timestamp))

    def clear(self):
        self.vertices.clear()

    def copy(self):
        newone = type(self)()
        newone.vertices = self.vertices.copy()
        return newone

    def start_pos(self):
        if len(self.vertices) == 0:
            raise IndexError
        return self.vertices[0]

    def end_pos(self):
        if len(self.vertices) == 0:
            raise IndexError

        return self.vertices[-1]

    def rot(self, v, rot):
        co = np.cos(rot)
        si = np.sin(rot)
        xx = co * v.x - si * v.y
        yy = si * v.x + co * v.y
        return TimedPosition(xx, yy, v.timestamp)

    def morph(self, start, end):
        path = Path()
        end_np = np.array(self.end_pos().pos(), dtype=float)
        start_np = np.array(self.start_pos().pos(), dtype=float)

        for point in self.vertices:
            nparr = np.array(point.pos(), dtype=float)

            dir_old = np.subtract(end_np, start_np)
            dir_new = np.subtract(np.array(end, dtype=float), np.array(start, dtype=float))
            magdiff = np.linalg.norm(dir_new) / np.linalg.norm(dir_old)
            nparr = nparr * magdiff
            path.add(nparr[0], nparr[1], point.timestamp)

        current_end = np.array(path.end_pos().pos(), dtype=float)
        current_start = np.array(path.start_pos().pos(), dtype=float)
        current_start_to_end = np.subtract(current_end, current_start)

        new_end = np.array(end, dtype=float)
        new_start = np.array(start, dtype=float)
        new_start_to_end = np.subtract(new_end, new_start)

        current_start_to_end = current_start_to_end / np.linalg.norm(current_start_to_end)
        new_start_to_end = new_start_to_end / np.linalg.norm(new_start_to_end)

        angle = np.arccos(np.clip(np.dot(current_start_to_end, new_start_to_end), -math.pi, math.pi))

        for p in path.vertices:
            rotated = self.rot(p, angle)
            p.x = rotated.x
            p.y = rotated.y

        translation = np.subtract(new_start, start_np)
        for p in path.vertices:
            _p = np.array(p.pos(), dtype=float)
            _p = _p + translation
            p.x = _p[0]
            p.y = _p[1]

        return path

    def __repr__(self):
        return f"Path({self.vertices})"

    def __len__(self):
        return len(self.vertices)


class PathCollection(object):
    def __init__(self, resolution):
        self.paths = []
        self.resolution = resolution

    def add(self, path, resolution):
        if resolution.width != self.resolution.width or resolution.height != self.resolution.height:
            raise Exception('New resolution is different to current. This should be handled somehow ..')
        self.paths.append(path)

    def __repr__(self):
        return f"PathCollection({self.resolution}, {self.paths})"

    def min(self):
        all_chained = [point for path in self.paths for point in path.vertices]
        minx = min(all_chained, key = lambda pos: pos.x).x
        miny = min(all_chained, key = lambda pos: pos.y).y
        return minx, miny

    def max(self):
        all_chained = [point for path in self.paths for point in path.vertices]
        maxx = max(all_chained, key=lambda pos: pos.x).x
        maxy = max(all_chained, key=lambda pos: pos.y).y
        return maxx, maxy