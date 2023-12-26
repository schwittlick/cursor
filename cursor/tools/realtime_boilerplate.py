import math
import logging

import arcade.color

from cursor.device import PaperSize, PlotterType
from cursor.export import ExportWrapper
from cursor.path import Path
from cursor.renderer.realtime import RealtimeRenderer


class Boilerplate(RealtimeRenderer):
    def __init__(self):
        dimension = 1000

        super().__init__(dimension, dimension, "boilerplate")
        self.background(arcade.color.WHITE)

        self.add_cb(arcade.key.R, self.new, long_press=False)
        self.add_cb(arcade.key.H, self.export_hpgl, long_press=False)

        self.new(self)

    def new(self, rr: RealtimeRenderer):
        rr.clear_list()

        logging.info(f"Generating new {self.title} geometry")

        # todo: generate geometry here
        p = Path.from_tuple_list([(0, 0), (500, 500), (0, 500)])

        # todo: add to realtime rendering
        rr.add_path(p)

    def export_hpgl(self, rr: RealtimeRenderer):
        # todo: prepare geometry for other rendering
        c = rr.collection.copy()

        c.rot(math.pi / 2)

        ExportWrapper().ex(
            c,
            PlotterType.HP_7550A,
            PaperSize.LANDSCAPE_A3,
            25,
            f"{self.title}",
            "version123",
            keep_aspect_ratio=False,
        )

    def on_update(self, delta_time: float):
        super().on_update(delta_time)

    def on_draw(self):
        super().on_draw()


if __name__ == "__main__":
    boilerplate = Boilerplate()
    boilerplate.run()
