import cursor.path as path

import sys
import wasabi
import time
import copy
import typing
from operator import itemgetter

log = wasabi.Printer()


class Sorter:
    SHANNON_X = 1
    SHANNON_Y = 2
    SHANNON_DIRECTION_CHANGES = 3
    DISTANCE = 4
    HASH = 5
    LAYER = 6
    PEN_SELECT = 7
    POINT_COUNT = 8
    FRECHET_DISTANCE = 9

    def __init__(self, reverse=False, param=SHANNON_X):
        self.__reverse = reverse
        self.__param = param

    @property
    def param(self):
        return self.__param

    @param.setter
    def param(self, v):
        self.__param = v

    def sort(self, paths: typing.List, reference_path: "path.Path" = None):
        t0 = time.time()
        if self.__param is self.SHANNON_X:
            paths.sort(key=lambda x: x.shannon_x, reverse=self.__reverse)
        elif self.__param is self.SHANNON_Y:
            paths.sort(key=lambda x: x.shannon_y, reverse=self.__reverse)
        elif self.__param is self.SHANNON_DIRECTION_CHANGES:
            paths.sort(
                key=lambda x: x.shannon_direction_changes, reverse=self.__reverse
            )
        elif self.__param is self.DISTANCE:
            paths.sort(key=lambda x: x.distance, reverse=self.__reverse)
        elif self.__param is self.HASH:
            paths.sort(key=lambda x: x.hash, reverse=self.__reverse)
        elif self.__param is self.LAYER:
            paths.sort(key=lambda x: x.layer, reverse=self.__reverse)
        elif self.__param is self.PEN_SELECT:
            paths.sort(key=lambda x: x.pen_select, reverse=self.__reverse)
        elif self.__param is self.POINT_COUNT:
            paths.sort(key=lambda x: len(x), reverse=self.__reverse)
        elif self.__param is self.FRECHET_DISTANCE and reference_path is not None:
            distances = []
            idx = 0
            for pa in paths:
                distances.append(
                    (idx, pa.frechet_similarity(reference_path), pa.copy())
                )
                idx += 1

            print(1)
            sorted_idxes = sorted(distances, key=itemgetter(1), reverse=self.__reverse)
            print(2)
            newlist = []
            for element in sorted_idxes:
                idx = element[0]
                newlist.append(element[2])
                # newlist[idx] = element[2].copy()

            paths = newlist
            # paths.sort(
            #    key=lambda n: n.frechet_similarity(reference_path),
            #    reverse=self.__reverse,
            # )
        else:
            raise Exception(
                f"Unknown parameter {self.__param} for {__class__.__name__}"
            )
        elapsed = time.time() - t0
        log.good(f"Sorted via {__class__.__name__} took {round(elapsed * 1000)}ms.")

    def sorted(self, paths: typing.List, reference_path=None):
        t0 = time.time()
        if self.__param is self.SHANNON_X:
            sorted_list = sorted(
                paths, key=lambda x: x.shannon_x, reverse=self.__reverse
            )
        elif self.__param is self.SHANNON_Y:
            sorted_list = sorted(
                paths, key=lambda x: x.shannon_y, reverse=self.__reverse
            )
        elif self.__param is self.SHANNON_DIRECTION_CHANGES:
            sorted_list = sorted(
                paths,
                key=lambda x: x.shannon_direction_changes,
                reverse=self.__reverse,
            )
        elif self.__param is self.DISTANCE:
            sorted_list = sorted(
                paths, key=lambda x: x.distance, reverse=self.__reverse
            )
        elif self.__param is self.HASH:
            sorted_list = sorted(paths, key=lambda x: x.hash, reverse=self.__reverse)
        elif self.__param is self.LAYER:
            sorted_list = sorted(paths, key=lambda x: x.layer, reverse=self.__reverse)
        elif self.__param is self.PEN_SELECT:
            sorted_list = sorted(
                paths, key=lambda x: x.pen_select, reverse=self.__reverse
            )
        elif self.__param is self.POINT_COUNT:
            sorted_list = sorted(paths, key=lambda x: len(x), reverse=self.__reverse)
        elif self.__param is self.FRECHET_DISTANCE and reference_path is not None:
            distances = []
            idx = 0
            for pa in paths:
                distances.append(
                    (idx, pa.frechet_similarity(reference_path), pa.copy())
                )
                idx += 1

            print(1)
            sorted_idxes = sorted(distances, key=itemgetter(1), reverse=self.__reverse)
            print(2)
            sorted_list = []
            for element in sorted_idxes:
                idx = element[0]
                sorted_list.append(element[2])
                # newlist[idx] = element[2].copy()
        else:
            raise Exception(f"Wrong param {self.__param} for {__class__.__name__}")
        elapsed = time.time() - t0
        log.good(f"Sorted via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        return sorted_list


class Filter:
    def filter(self, paths):
        raise NotImplementedError("Not implemented in base class")

    def filtered(self, paths):
        raise NotImplementedError("Not implemented in base class")


class EntropyMinFilter(Filter):
    def __init__(self, min_x_entropy, min_y_entropy):
        self.min_x = min_x_entropy
        self.min_y = min_y_entropy

    def filter(self, paths):
        t0 = time.time()
        len_before = len(paths)
        paths[:] = [
            p for p in paths if p.shannon_x > self.min_x and p.shannon_y > self.min_y
        ]
        len_after = len(paths)

        elapsed = time.time() - t0
        log.good(f"Filtering via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


class EntropyMaxFilter(Filter):
    def __init__(self, max_x_entropy, max_y_entropy):
        self.max_x = max_x_entropy
        self.max_y = max_y_entropy

    def filter(self, paths):
        t0 = time.time()
        len_before = len(paths)

        paths[:] = [
            p for p in paths if p.shannon_x < self.max_x and p.shannon_y < self.max_y
        ]

        len_after = len(paths)
        elapsed = time.time() - t0
        log.good(f"Filtering via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


class DirectionChangeEntropyFilter(Filter):
    def __init__(self, min_entropy, max_entropy):
        self.min = min_entropy
        self.max = max_entropy

    def filter(self, paths):
        t0 = time.time()
        len_before = len(paths)

        paths[:] = [
            p for p in paths if self.max > p.shannon_direction_changes > self.min
        ]

        len_after = len(paths)
        elapsed = time.time() - t0
        log.good(f"Filtering via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


class BoundingBoxFilter(Filter):
    def __init__(self, bb):
        self.bb = bb

    def filter(self, paths):
        paths[:] = [p for p in paths if p.inside(self.bb)]


class MinPointCountFilter(Filter):
    def __init__(self, point_count):
        self.point_count = point_count

    def filter(self, paths):
        t0 = time.time()
        len_before = len(paths)

        paths[:] = [p for p in paths if len(p) >= self.point_count]

        len_after = len(paths)
        elapsed = time.time() - t0
        log.good(f"Filtering via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        log.good(
            f"{__class__.__name__}: reduced path count from {len_before} to {len_after}"
        )

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


class MaxPointCountFilter(Filter):
    def __init__(self, point_count):
        self.point_count = point_count

    def filter(self, paths):
        t0 = time.time()
        len_before = len(paths)

        paths[:] = [p for p in paths if len(p) <= self.point_count]

        len_after = len(paths)
        elapsed = time.time() - t0
        log.good(f"Filtering via {__class__.__name__} took {round(elapsed * 1000)}ms.")
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
        len_before = len(paths)

        for pa in paths:
            verts = []
            for pi in range(len(pa) - 1):
                p1 = pa[pi]
                p2 = pa[pi + 1]
                d = p1.distance(p2)
                if self.min_distance <= d <= self.max_distance:
                    verts.append(p2)
            pa.vertices = verts
            pa.clean()

        len_after = len(paths)
        log.good(
            f"DistanceBetweenPointsFilter: reduced path count from {len_before} to {len_after}"
        )


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
