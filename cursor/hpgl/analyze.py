import logging
import pathlib
from argparse import ArgumentParser
from enum import Enum

from cursor.collection import Collection
from cursor.hpgl.parser import HPGLParser


def calc_number_of_dots(collection: Collection) -> int:
    number_of_points = 0
    for path in collection:
        if len(path) == 2:
            if path[0] == path[1]:
                number_of_points += 1

    return number_of_points


def calc_time_to_plot_seconds(collection: Collection) -> int:
    pass


class Pen(Enum):
    PEN1 = 1
    PEN2 = 2
    PEN3 = 3
    PEN4 = 4
    PEN5 = 5
    PEN6 = 6
    PEN7 = 7
    PEN8 = 8


class PenData:
    def __init__(self, pd: int = 0, pu: int = 0, dots: int = 0):
        self.pen_up_in_meter = pu
        self.pen_down_in_meter = pd
        self.number_of_dots = dots

    def __str__(self) -> str:
        return f"pen-down {self.pen_down_in_meter}m pen-up {self.pen_up_in_meter}m dots {self.number_of_dots}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other):
        return (
            self.pen_down_in_meter == other.pen_down_in_meter
            and self.pen_up_in_meter == other.pen_up_in_meter
            and self.number_of_dots == other.number_of_dots
        )


class HPGLAnalyzeData:
    def __init__(
        self,
        total_pen_up: int = 0,
        total_pen_down: int = 0,
        total_number_of_dots: int = 0,
        total_time_to_plot: int = 0,
    ):
        self.total_pen_up = total_pen_up
        self.total_pen_down = total_pen_down
        self.total_number_of_dots = total_number_of_dots
        self.total_time_to_plot = total_time_to_plot

        self.data_per_pen = {
            Pen.PEN1: PenData(),
            Pen.PEN2: PenData(),
            Pen.PEN3: PenData(),
            Pen.PEN4: PenData(),
            Pen.PEN5: PenData(),
            Pen.PEN6: PenData(),
            Pen.PEN7: PenData(),
            Pen.PEN8: PenData(),
        }

    def __str__(self) -> str:
        return (
            f"Total pen-up {self.total_pen_up}m pen-down {self.total_pen_down}m "
            f"dots {self.total_number_of_dots} per_pen {self.data_per_pen} "
            f"time {self.total_time_to_plot}s"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other):
        return (
            self.total_pen_up == other.total_pen_up
            and self.total_pen_down == other.total_pen_down
            and self.total_number_of_dots == other.total_number_of_dots
            and int(self.total_time_to_plot) == int(other.total_time_to_plot)
            and self.data_per_pen == other.data_per_pen
        )


class HPGLAnalyzer:
    def __init__(self):
        pass

    def analyze_collection(self, collection: Collection) -> HPGLAnalyzeData:
        # detect format somehow?
        # does BB fit into A1, A3 etc?

        total_pen_up = int(collection.calc_pen_up_distance(40) / 1000)
        total_pen_down = int(collection.calc_pen_down_distance(40) / 1000)
        number_of_points = calc_number_of_dots(collection)

        data = HPGLAnalyzeData()
        data.total_pen_up = total_pen_up
        data.total_pen_down = total_pen_down
        data.total_number_of_dots = number_of_points
        # 80 is the maximum speed on some machines. this is not really accurate in the generally
        data.total_time_to_plot = (collection.calc_pen_up_distance(40) / 100) / 80
        for pa in collection:
            velocity = (
                pa.velocity if pa.velocity else 1.0
            )  # this here assumes a hp7550a
            data.total_time_to_plot += ((pa.distance / 40) / 100) / velocity

        split_by_pens = {key + 1: Collection() for key in range(8)}
        [split_by_pens[path.pen_select].add(path) for path in collection]

        for key, val in split_by_pens.items():
            total_pen_up = int(val.calc_pen_up_distance(40) / 1000)
            total_pen_down = int(val.calc_pen_down_distance(40) / 1000)
            numer_of_dots = calc_number_of_dots(val)

            data.data_per_pen[Pen(key)] = PenData(
                total_pen_down, total_pen_up, numer_of_dots
            )

        return data

    def analyze(self, hpgl_path: pathlib.Path) -> HPGLAnalyzeData:
        hpgl_file_path = pathlib.Path(hpgl_path)

        parser = HPGLParser()
        parsed = parser.parse(hpgl_file_path)
        return self.analyze_collection(parsed)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("hpgl_file")
    args = parser.parse_args()

    analyzer = HPGLAnalyzer()
    data = analyzer.analyze(args.hpgl_file)
    logging.info(data)

    # INFO: Total pen-up: 1044690m
    # INFO: Total pen-down: 517630m
