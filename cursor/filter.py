import wasabi
import time
import copy

log = wasabi.Printer()


class Sorter:
    SHANNON_X = 1
    SHANNON_Y = 2
    SHANNON_DIRECTION_CHANGES = 3
    DISTANCE = 4
    HASH = 5

    def __init__(self, reverse=False, param=SHANNON_X):
        self.__reverse = reverse
        self.__param = param

    @property
    def param(self):
        return self.__param

    @param.setter
    def param(self, v):
        self.__param = v

    def sort(self, paths):
        if isinstance(paths, list):
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
            else:
                raise Exception(
                    f"Unknown parameter {self.__param} for {__class__.__name__}"
                )
            elapsed = time.time() - t0
            log.good(f"Sorted via {__class__.__name__} took {round(elapsed * 1000)}ms.")
        else:
            raise Exception(f"Only pass list objects to this {__class__.__name__}")

    def sorted(self, paths):
        if isinstance(paths, list):
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
                sorted_list = sorted(
                    paths, key=lambda x: x.hash, reverse=self.__reverse
                )
            else:
                raise Exception(
                    f"Wrong param {self.__param} for {__class__.__name__}"
                )
            elapsed = time.time() - t0
            log.good(f"Sorted via {__class__.__name__} took {round(elapsed * 1000)}ms.")
            return sorted_list
        else:
            raise Exception(f"Only pass list objects to this {__class__.__name__}")


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


class BoundingBoxFilter(Filter):
    def __init__(self, bb):
        self.bb = bb

    def filter(self, paths):
        paths[:] = [p for p in paths if self.bb.inside(p)]


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
