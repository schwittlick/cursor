"""
vbo to render a line

"""

import arcade

from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from cursor.renderer import RealtimeRenderer


p = DataDirHandler().recordings()
ll = Loader(directory=p, limit_files=1)
all_paths = ll.all_paths()


SCREEN_TITLE = "simple arcade cursor realtime example"


def add_random_path(renderer: RealtimeRenderer):
    p1 = all_paths.random()
    p1.scale(renderer.width, renderer.height)

    renderer.add_path(p1)


def main():

    r = RealtimeRenderer(1920, 1080, SCREEN_TITLE)
    r.add_cb(arcade.key.R, add_random_path)

    RealtimeRenderer.run()


if __name__ == "__main__":
    main()
