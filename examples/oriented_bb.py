import arcade

from cursor.bb import BoundingBox
from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from cursor.renderer import RealtimeRenderer

p = DataDirHandler().recordings()
ll = Loader(directory=p, limit_files=1)
all_paths = ll.all_paths()

SCREEN_TITLE = "oriented bounding box"


def add_random_path(renderer: RealtimeRenderer):
    renderer.clear_list()

    p1 = all_paths.random()
    p1.transform(p1.bb(), BoundingBox(0, 0, 1920, 1080))

    p2 = p1.rotated_into_bb(BoundingBox(0, 0, 1920, 1080))

    renderer.add_path(p1, line_width=5, color=arcade.color.BLACK)
    renderer.add_path(p2, line_width=5, color=arcade.color.RED)


def main():
    r = RealtimeRenderer(1920, 1080, SCREEN_TITLE)
    r.background(arcade.color.WHITE)
    r.add_cb(arcade.key.R, add_random_path, long_press=False)

    RealtimeRenderer.run()


if __name__ == "__main__":
    main()
