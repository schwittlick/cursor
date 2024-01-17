import logging
import pathlib
from argparse import ArgumentParser

from cursor.collection import Collection
from cursor.hpgl.parser import HPGLParser


class HPGLAnalyzer:
    def __init__(self):
        pass

    def analyze(self, hpgl_path: pathlib.Path):
        hpgl_file_path = pathlib.Path(hpgl_path)

        parser = HPGLParser()
        parsed = parser.parse(hpgl_file_path)

        # detect format somehow?
        # does BB fit into A1, A3 etc?

        total_pen_up = int(parsed.calc_pen_up_distance(40))
        total_pen_down = int(parsed.calc_pen_down_distance(40))

        logging.info(f"Total pen-up: {total_pen_up}m")
        logging.info(f"Total pen-down: {total_pen_down}m")

        split_by_pens = {key + 1: Collection() for key in range(8)}

        [split_by_pens[path.pen_select].add(path) for path in parsed]

        for key, val in split_by_pens.items():
            total_pen_up = int(val.calc_pen_up_distance(40))
            total_pen_down = int(val.calc_pen_down_distance(40))
            logging.info(f"Pen {key}")
            logging.info(f"pen-up: {total_pen_up}m")
            logging.info(f"pen-down: {total_pen_down}m")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('hpgl_file')
    args = parser.parse_args()

    analyzer = HPGLAnalyzer()
    analyzer.analyze(args.hpgl_file)

    # INFO: Total pen-up: 1044690m
    # INFO: Total pen-down: 517630m
