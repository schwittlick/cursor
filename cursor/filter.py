class Filter:
    def filter(self, paths):
        raise NotImplementedError("Not implemented in base class")


class EntropyFilter(Filter):
    def __init__(self, max_x_entropy, max_y_entropy):
        self.max_x = max_x_entropy
        self.max_y = max_y_entropy

    def filter(self, paths):
        len_before = len(paths)
        paths[:] = [p for p in paths if not p.shannon_x() < self.max_x and p.shannon_y() < self.max_y]
        len_after = len(paths)
        print(F"EntropyFilter: reduced path count from {len_before} to {len_after}")


class BoundingBoxFilter(Filter):
    def __init__(self, bb):
        self.bb = bb

    def filter(self, paths):
        paths[:] = [p for p in paths if self.bb.inside(p)]


class MinPointCountFilter(Filter):
    def __init__(self, point_count):
        self.point_count = point_count

    def filter(self, paths):
        paths[:] = [p for p in paths if len(p) >= self.point_count]


class MaxPointCountFilter(Filter):
    def __init__(self, point_count):
        self.point_count = point_count

    def filter(self, paths):
        paths[:] = [p for p in paths if len(p) <= self.point_count]


class DistanceFilter(Filter):
    def __init__(self, max_distance, res):
        self.max_distance = max_distance
        self.res = res

    def filter(self, paths):
        len_before = len(paths)
        paths[:] = [p for p in paths if p.distance(self.res) <= self.max_distance]
        len_after = len(paths)
        print(F"DistanceFilter: reduced path count from {len_before} to {len_after}")
