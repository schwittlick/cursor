from enum import Enum, auto
from operator import itemgetter
from typing import List, Optional

from cursor.algorithm import frechet
from cursor.path import Path
from cursor.timer import timing


# noinspection PyArgumentList
class SortParameter(Enum):
    # https://de.wikipedia.org/wiki/Auff%C3%A4lligkeit_(Informationstheorie)
    ENTROPY_X = auto()
    ENTROPY_Y = auto()
    ENTROPY_CROSS = auto()
    ENTROPY_DIRECTION_CHANGES = auto()
    DISTANCE = auto()
    DURATION = auto()
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
    def __init__(self, reverse: bool = False, param: SortParameter = SortParameter.ENTROPY_X):
        self.__reverse = reverse
        self.__param = param

    @property
    def param(self) -> SortParameter:
        return self.__param

    @param.setter
    def param(self, v: SortParameter) -> None:
        self.__param = v

    @timing
    def sort(
            self,
            paths: List[Path],
            reference_path: Optional[Path] = None,
    ) -> None:
        if self.__param is SortParameter.ENTROPY_X:
            paths.sort(key=lambda x: x.entropy_x, reverse=self.__reverse)
        elif self.__param is SortParameter.ENTROPY_Y:
            paths.sort(key=lambda x: x.entropy_y, reverse=self.__reverse)
        elif self.__param is SortParameter.ENTROPY_CROSS:
            paths.sort(key=lambda x: x.entropy_y *
                       x.entropy_x, reverse=self.__reverse)
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_X:
            paths.sort(key=lambda x: x.differential_entropy_x,
                       reverse=self.__reverse)
        elif self.__param is SortParameter.DIFFERENTIAL_ENTROPY_Y:
            paths.sort(key=lambda x: x.differential_entropy_y,
                       reverse=self.__reverse)
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

    @timing
    def sorted(
            self,
            paths: List[Path],
            reference_path: Optional[Path] = None,
    ) -> List[Path]:
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
            sorted_list = sorted(
                paths, key=lambda x: x.hash, reverse=self.__reverse)
        elif self.__param is SortParameter.LAYER:
            sorted_list = sorted(
                paths, key=lambda x: x.layer, reverse=self.__reverse)
        elif self.__param is SortParameter.PEN_SELECT:
            sorted_list = sorted(
                paths, key=lambda x: x.pen_select, reverse=self.__reverse
            )
        elif self.__param is SortParameter.POINT_COUNT:
            sorted_list = sorted(
                paths, key=lambda x: len(x), reverse=self.__reverse)
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
                distances = frechet.frechet_multiprocessing(
                    paths, reference_path)
            else:
                distances = [
                    (index, item.frechet_similarity(reference_path), item)
                    for index, item in enumerate(paths)
                ]

            sorted_idxes = sorted(
                distances, key=itemgetter(1), reverse=self.__reverse)
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
            raise Exception(
                f"Wrong param {self.__param} for {__class__.__name__}")
        return sorted_list
