import numpy as np


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

    def morph(self, start, end):
        path = Path()
        for point in self.vertices:
            nparr = np.array(point)
            end_np = np.array(self.end_pos().pos())
            start_np = np.array(self.start_pos().pos())
            print(end_np)
            print(start_np)
            dir_old = np.subtract(end_np, start_np)
            dir_new = np.subtract(np.array(start), np.array(end))
            print(dir_old)
            print(dir_new)

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