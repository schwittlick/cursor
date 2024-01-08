import math
import logging

import arcade.color

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.device import PaperSize, PlotterType
from cursor.export import ExportWrapper
from cursor.path import Path
from cursor.renderer.realtime import RealtimeRenderer


class RealtimeDropin(RealtimeRenderer):
    def __init__(self, collection: Collection):
        out = BoundingBox(0, 0, 1920, 1080)
        super().__init__(int(out.w), int(out.h), "temp")
        self.background(arcade.color.WHITE)

        collection.transform(out)
        self.add_collection(collection, line_width=3, color=arcade.color.BLACK)
        self.run()


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

        wrapper = ExportWrapper(
            c,
            PlotterType.HP_7550A,
            PaperSize.LANDSCAPE_A3,
            25,
            f"{self.title}",
            "version123",
            keep_aspect_ratio=False)
        wrapper.fit()
        wrapper.ex()

    def on_update(self, delta_time: float):
        super().on_update(delta_time)

    def on_draw(self):
        super().on_draw()


if __name__ == "__main__":
    boilerplate = Boilerplate()
    boilerplate.run()
