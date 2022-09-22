from cursor.path import Path
from cursor.misc import Timer
from cursor.algorithm import frechet

import sys
import wasabi
import copy
import typing
from enum import Enum, auto
from operator import itemgetter

log = wasabi.Printer()


# noinspection PyArgumentList
class SortParameter(Enum):
    # https://de.wikipedia.org/wiki/Auff%C3%A4lligkeit_(Informationstheorie)
    ENTROPY_X = auto()
    ENTROPY_Y = auto()
    ENTROPY_CROSS = auto()
    ENTROPY_DIRECTION_CHANGES = auto()
    DISTANCE = auto()
    HASH = auto()
    LAYER = auto()
    PEN_SELECT = auto()
    POINT_COUNT = auto()
    FRECHET_DISTANCE = auto()
    DIFFERENTIAL_ENTROPY_X = auto()
    DIFFERENTIAL_ENTROPY_Y = auto()
    DIFFERENTIAL_ENTROPY_CROSS = auto()
    VARIATION_X = auto()
    VARIATION_Y = auto()


class Sorter:
    def __init__(self, reverse=False, param=SortParameter.ENTROPY_X):
        self.__reverse = reverse
        self.__param = param

    @property
    def param(self):
        return self.__param

    @param.setter
    def param(self, v):
        self.__param = v

    def sort(
        self,
        paths: typing.List[Path],
        reference_path: Path = None,
    ):
        t = Timer()
        t.start()
        if self.__param is SortParameter.ENTROPY_X:
            paths.sort(key=lambda x: x.entropy_x, reverse=self.__reverse)
        elif self.__param is SortParameter.ENTROPY_Y:
            paths.sort(key=lambda x: x.entropy_y, reverse=self.__reverse)
        elif self.__param is SortParameter.ENTROPY_CROSS:
            paths.sort(key=lambda x: x.entropy_y * x.entropy_x, reverse=self.__reverse)
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_X:
            paths.sort(key=lambda x: x.differential_entropy_x, reverse=self.__reverse)
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_Y:
            paths.sort(key=lambda x: x.differential_entropy_y, reverse=self.__reverse)
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_CROSS:
            paths.sort(
                key=lambda x: x.differential_entropy_x * x.differential_entropy_y,
                reverse=self.__reverse,
            )
        elif self.__param is SortParameter.ENTROPY_DIRECTION_CHANGES:
            paths.sort(
                key=lambda x: x.entropy_direction_changes, reverse=self.__reverse
            )
        elif self.__param is SortParameter.DISTANCE:
            paths.sort(key=lambda x: x.distance, reverse=self.__reverse)
        elif self.__param is SortParameter.HASH:
            paths.sort(key=lambda x: x.hash, reverse=self.__reverse)
        elif self.__param is SortParameter.LAYER:
            paths.sort(key=lambda x: x.layer, reverse=self.__reverse)
        elif self.__param is SortParameter.PEN_SELECT:
            paths.sort(key=lambda x: x.pen_select, reverse=self.__reverse)
        elif self.__param is SortParameter.POINT_COUNT:
            paths.sort(key=lambda x: len(x), reverse=self.__reverse)
        elif (
            self.__param is SortParameter.FRECHET_DISTANCE
            and reference_path is not None
        ):
            raise Exception("Can't sort by Frechet Distance in-place. (yet)")
        elif self.__param is SortParameter.VARIATION_X:
            paths.sort(key=lambda x: x.variation_x, reverse=self.__reverse)
        elif self.__param is SortParameter.VARIATION_Y:
            paths.sort(key=lambda x: x.variation_y, reverse=self.__reverse)
        else:
            raise Exception(
                f"Unknown parameter {self.__param} for {__class__.__name__}"
            )
        t.print_elapsed(f"Sorted via {__class__.__name__} took ")

    def sorted(
        self,
        paths: typing.List[Path],
        reference_path: Path = None,
    ):
        t = Timer()
        t.start()
        if self.__param is SortParameter.ENTROPY_X:
            sorted_list = sorted(
                paths, key=lambda x: x.entropy_x, reverse=self.__reverse
            )
        elif self.__param is SortParameter.ENTROPY_Y:
            sorted_list = sorted(
                paths, key=lambda x: x.entropy_y, reverse=self.__reverse
            )
        elif self.__param is SortParameter.ENTROPY_CROSS:
            sorted_list = sorted(
                paths, key=lambda x: x.entropy_y * x.entropy_x, reverse=self.__reverse
            )
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_X:
            sorted_list = sorted(
                paths, key=lambda x: x.differential_entropy_x, reverse=self.__reverse
            )
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_Y:
            sorted_list = sorted(
                paths, key=lambda x: x.differential_entropy_y, reverse=self.__reverse
            )
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_CROSS:
            sorted_list = sorted(
                paths,
                key=lambda x: x.differential_entropy_x * x.differential_entropy_y,
                reverse=self.__reverse,
            )
        elif self.__param is SortParameter.ENTROPY_DIRECTION_CHANGES:
            sorted_list = sorted(
                paths,
                key=lambda x: x.entropy_direction_changes,
                reverse=self.__reverse,
            )
        elif self.__param is SortParameter.DISTANCE:
            sorted_list = sorted(
                paths, key=lambda x: x.distance, reverse=self.__reverse
            )
        elif self.__param is SortParameter.HASH:
            sorted_list = sorted(paths, key=lambda x: x.hash, reverse=self.__reverse)
        elif self.__param is SortParameter.LAYER:
            sorted_list = sorted(paths, key=lambda x: x.layer, reverse=self.__reverse)
        elif self.__param is SortParameter.PEN_SELECT:
            sorted_list = sorted(
                paths, key=lambda x: x.pen_select, reverse=self.__reverse
            )
        elif self.__param is SortParameter.POINT_COUNT:
            sorted_list = sorted(paths, key=lambda x: len(x), reverse=self.__reverse)
        elif (
            self.__param is SortParameter.FRECHET_DISTANCE
            and reference_path is not None
        ):
            use_multiprocessing = False
            # don't use multiprocessing
            # transferring memory to processes takes too long
            # at least on windows duh
            # test this on unix with start_method='fork' method
            if use_multiprocessing:
                distances = frechet.frechet_multiprocessing(paths, reference_path)
            else:
                distances = [
                    (index, item.frechet_similarity(reference_path), item)
                    for index, item in enumerate(paths)
                ]

            sorted_idxes = sorted(distances, key=itemgetter(1), reverse=self.__reverse)
            sorted_list = [el[2] for el in sorted_idxes]
        elif self.__param is SortParameter.VARIATION_X:
            sorted_list = sorted(
                paths, key=lambda x: x.variation_x, reverse=self.__reverse
            )
        elif self.__param is SortParameter.VARIATION_Y:
            sorted_list = sorted(
                paths, key=lambda x: x.variation_y, reverse=self.__reverse
            )
        else:
            raise Exception(f"Wrong param {self.__param} for {__class__.__name__}")
        log.good(f"Sorted via {__class__.__name__} took {round(t.elapsed() * 1000)}ms.")
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

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


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

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


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

    def filtered(self, paths):
        copied_paths = copy.deepcopy(paths)
        self.filter(copied_paths)
        return copied_paths


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
            pa.vertices = verts
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
