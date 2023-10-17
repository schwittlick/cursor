from cursor.timer import Timer

import sys
import wasabi
import copy

log = wasabi.Printer()


class Filter:
    def filter(self, paths):
        raise NotImplementedError("Not implemented in base class")

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


class EntropyMinFilter(Filter):
    def __init__(self, min_x_entropy, min_y_entropy):
        self.min_x = min_x_entropy
        self.min_y = min_y_entropy

    def filter(self, paths):
        t = Timer()
        t.start()
        len_before = len(paths)
        paths[:] = [
            p for p in paths if p.entropy_x > self.min_x and p.entropy_y > self.min_y
        ]
        len_after = len(paths)

        log.good(
            f"Filtering via {__class__.__name__} took {round(t.elapsed() * 1000)}ms."
        )
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )


class EntropyMaxFilter(Filter):
    def __init__(self, max_x_entropy, max_y_entropy):
        self.max_x = max_x_entropy
        self.max_y = max_y_entropy

    def filter(self, paths):
        t = Timer()
        t.start()
        len_before = len(paths)

        paths[:] = [
            p for p in paths if p.entropy_x < self.max_x and p.entropy_y < self.max_y
        ]

        len_after = len(paths)
        elapsed = t.elapsed()
        log.good(f"Filtering via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )


class DirectionChangeEntropyFilter(Filter):
    def __init__(self, min_entropy, max_entropy):
        self.min = min_entropy
        self.max = max_entropy

    def filter(self, paths):
        t = Timer()
        t.start()
        len_before = len(paths)

        paths[:] = [
            p for p in paths if self.max > p.entropy_direction_changes > self.min
        ]

        len_after = len(paths)
        log.good(
            f"Filtering via {__class__.__name__} took {round(t.elapsed() * 1000)}ms."
        )
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )


class BoundingBoxFilter(Filter):
    def __init__(self, bb):
        self.bb = bb

    def filter(self, paths):
        paths[:] = [p for p in paths if p.inside(self.bb)]


class MinPointCountFilter(Filter):
    def __init__(self, point_count):
        self.point_count = point_count

    def filter(self, paths):
        t = Timer()
        t.start()
        len_before = len(paths)

        paths[:] = [p for p in paths if len(p) >= self.point_count]

        len_after = len(paths)
        log.good(
            f"Filtering via {__class__.__name__} took {round(t.elapsed() * 1000)}ms."
        )
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )


class MaxPointCountFilter(Filter):
    def __init__(self, point_count):
        self.point_count = point_count

    def filter(self, paths):
        t = Timer()
        t.start()
        len_before = len(paths)

        paths[:] = [p for p in paths if len(p) <= self.point_count]

        len_after = len(paths)
        log.good(
            f"Filtering via {__class__.__name__} took {round(t.elapsed() * 1000)}ms."
        )
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )


class DistanceFilter(Filter):
    def __init__(self, max_distance):
        self.max_distance = max_distance

    def filter(self, paths):
        len_before = len(paths)
        paths[:] = [p for p in paths if p.distance <= self.max_distance]
        len_after = len(paths)
        log.good(f"DistanceFilter: reduced path count from {len_before} to {len_after}")


class AspectRatioFilter(Filter):
    def __init__(self, min_as, max_as=sys.maxsize):
        self.min_as = min_as
        self.max_as = max_as

    def filter(self, paths):
        len_before = len(paths)
        paths[:] = [p for p in paths if self.min_as < p.aspect_ratio() < self.max_as]
        len_after = len(paths)
        log.good(
            f"AspectRatioFilter: reduced path count from {len_before} to {len_after}"
        )


class DistanceBetweenPointsFilter(Filter):
    def __init__(self, min_distance, max_distance):
        self.min_distance = min_distance
        self.max_distance = max_distance

    def filter(self, paths):
        t = Timer()
        t.start()
        len_before = len(paths)

        for pa in paths:
            verts = []
            for pi in range(len(pa) - 1):
                p1 = pa[pi]
                p2 = pa[pi + 1]
                d = p1.distance(p2)
                if self.min_distance <= d <= self.max_distance:
                    verts.append(p2)
            pa.generate = verts
            pa.clean()

        len_after = len(paths)
        log.good(
            f"DistanceBetweenPointsFilter: reduced path count from {len_before} to {len_after}"
        )

        log.good(f"This took {t.elapsed()}s")


class MinTravelDistanceFilter(Filter):
    def __init__(self, min_distance):
        self.min_distance = min_distance

    def filter(self, paths):
        len_before = len(paths)
        paths[:] = [p for p in paths if p.distance > self.min_distance]
        len_after = len(paths)
        log.good(
            f"MinDistanceFilter: reduced path count from {len_before} to {len_after}"
        )
