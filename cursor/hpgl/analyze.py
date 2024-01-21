import logging
import pathlib
from argparse import ArgumentParser
from enum import Enum, auto

from cursor.collection import Collection
from cursor.hpgl.parser import HPGLParser


def calc_number_of_dots(collection: Collection) -> int:
    number_of_points = 0
    for path in collection:
        if len(path) == 2:
            if path[0] == path[1]:
                number_of_points += 1

    return number_of_points


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
    def __init__(self):
        self.total_pen_up = 0
        self.total_pen_down = 0
        self.total_number_of_dots = 0

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
            f"Total pen-up {self.total_pen_up}m pen-down {self.total_pen_down}m dots "
            f"{self.total_number_of_dots} per_pen {self.data_per_pen}"
        )


class HPGLAnalyzer:
    def __init__(self):
        pass

    def analyze(self, hpgl_path: pathlib.Path) -> HPGLAnalyzeData:
        hpgl_file_path = pathlib.Path(hpgl_path)

        parser = HPGLParser()
        parsed = parser.parse(hpgl_file_path)

        # detect format somehow?
        # does BB fit into A1, A3 etc?

        total_pen_up = int(parsed.calc_pen_up_distance(40) / 1000)
        total_pen_down = int(parsed.calc_pen_down_distance(40) / 1000)
        number_of_points = calc_number_of_dots(parsed)

        data = HPGLAnalyzeData()
        data.total_pen_up = total_pen_up
        data.total_pen_down = total_pen_down
        data.total_number_of_dots = number_of_points

        split_by_pens = {key + 1: Collection() for key in range(8)}
        [split_by_pens[path.pen_select].add(path) for path in parsed]

        for key, val in split_by_pens.items():
            total_pen_up = int(val.calc_pen_up_distance(40) / 1000)
            total_pen_down = int(val.calc_pen_down_distance(40) / 1000)
            numer_of_dots = calc_number_of_dots(val)
            # logging.info(
            #    f"Pen {key}: pen-up {total_pen_up}m: pen-down {total_pen_down}m: dots: {numer_of_dots}"
            # )

            data.data_per_pen[Pen(key)] = PenData(
                total_pen_down, total_pen_up, numer_of_dots
            )

        return data


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("hpgl_file")
    args = parser.parse_args()

    analyzer = HPGLAnalyzer()
    data = analyzer.analyze(args.hpgl_file)
    logging.info(data)

    # INFO: Total pen-up: 1044690m
    # INFO: Total pen-down: 517630m
