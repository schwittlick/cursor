import arcade
import numpy as np
from HersheyFonts import HersheyFonts

from cursor import misc
from cursor.collection import Collection
from cursor.renderer import RealtimeRenderer
from cursor.timer import Timer
from tools.spline_experiment import transform_path
from tools.tests.lib import project

thefont = HersheyFonts()
thefont.load_default_font()
thefont.normalize_rendering(100)


def on_mouse(rr: RealtimeRenderer, x, y, dx, dy):
    timer = Timer()

    temp_points = []

    for (x1, y1), (x2, y2) in thefont.lines_for_text('HEYH'):
        temp_points.append([[x1, -y1, 0], [x2, -y2, 0]])

    print(rr)
    print(x, y, dx, dy)

    v1 = misc.map(x, 0, rr.width, -1, 1)
    v2 = misc.map(y, 0, rr.height, -1, 1)

    basis1 = np.array([1, 0, 0])
    basis2 = np.array([0, 1, 0])

    plane_point = np.array([0, 0, 0])
    plane_normal = np.array([v1, v2, 1])

    c = project(temp_points, plane_point, plane_normal, basis1, basis2)

    c_final = Collection()

    bb = c.bb()
    for p in c:
        c_final.add(transform_path(p, bb, ((0, 0), (800, 400))))
    rr.clear_list()
    rr.add_collection(c_final, line_width=2, color=arcade.color.GRAY)

    timer.print_elapsed()


if __name__ == "__main__":
    rr = RealtimeRenderer(800, 400, "projection")
    rr.background(arcade.color.WHITE)
    rr.set_on_mouse_cb(on_mouse)

    rr.run()
