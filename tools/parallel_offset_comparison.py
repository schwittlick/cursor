import arcade.color

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.renderer.realtime import RealtimeRenderer


class OffsetRenderer(RealtimeRenderer):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.set_on_mouse_cb(self.on_mouse_motion)

        recordings = DataDirHandler().recordings()
        _loader = Loader(directory=recordings, limit_files=1)
        self.paths = _loader.all_paths()
        self.path = self.paths.random()

        self.add_cb(arcade.key.N, self.new_path, False)

    def new_path(self, rr):
        self.path = self.paths.random()

    def on_mouse_motion(self, x, y, dx, dy):
        self.clear_list()

        padding = 10

        # path = Path.from_tuple_list([(0, 0), (1, 0), (2, 2), (1, 5), (3, 3)])
        self.path.transform(self.path.bb(),
                            BoundingBox(padding, padding, self.width / 4 - padding, self.height - padding))

        offset = x

        offset1 = self.path.parallel_offset(-offset)
        offset2 = self.path.offset(offset)
        offset3 = self.path.curve_offset(-offset)

        collection0 = Collection()
        collection1 = Collection()
        collection2 = Collection()
        collection3 = Collection()

        collection0.add(self.path)

        for pa in offset1:
            collection1.add(pa)
        collection2.add(offset2)
        for pa in offset3:
            collection3.add(pa)

        collection1.translate(self.width / 4, 0)
        collection2.translate(self.width / 4 * 2, 0)
        collection3.translate(self.width / 4 * 3, 0)

        self.add_collection(collection0, line_width=3, color=arcade.color.BLACK)
        self.add_collection(collection1, line_width=3, color=arcade.color.GREEN)
        self.add_collection(collection2, line_width=3, color=arcade.color.BLUE)
        self.add_collection(collection3, line_width=3, color=arcade.color.BLUE)


if __name__ == "__main__":
    renderer = OffsetRenderer(2400, 600, "offset")

    renderer.run()
