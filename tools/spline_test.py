import arcade
import splines

import matplotlib.pyplot as plt
import numpy as np

from cursor.collection import Collection
from cursor.device import Paper, PaperSize, PlotterType
from cursor.export import ExportWrapper
from cursor.position import Position
from cursor.renderer import RealtimeRenderer
from cursor.sorter import Sorter, SortParameter
from data.compositions.composition86 import transform_path
from tools.catmull_rom import catmull_rom

np.set_printoptions(precision=4)

from helper import plot_spline_2d, plot_tangent_2d

from cursor.path import Path

dimensions = Paper.sizes[PaperSize.LANDSCAPE_A4]


def test1():
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 1)
    pa.add(1, 1)
    pa.add(0, 1)
    pa.add(0, 0)

    p = transform_path(pa, pa.bb(), ((0, 0), (dimensions[0] * 4, dimensions[1] * 4)))

    s1 = splines.CatmullRom(p.as_tuple_list(), alpha=0, endconditions='closed')

    print(s1)

    out = Path()

    segs = s1.segments
    for seg in segs:
        for p in seg:
            out.add(p[0], p[1])
            print(p)

    p = transform_path(out, out.bb(), ((0, 0), (dimensions[0] * 4, dimensions[1] * 4)))
    c = Collection()
    c.add(p)

    rr = RealtimeRenderer(dimensions[0] * 4, dimensions[1] * 4, "spline")
    rr.set_bg_color(arcade.color.WHITE)
    rr.add_collection(c, line_width=1, color=arcade.color.GRAY)

    rr.run()


def test2():
    x = []
    y = []
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 1)
    pa.add(1, 1)
    pa.add(0, 1)
    pa.add(0, 0)

    for p in pa:
        x.append(p.x)
        y.append(p.y)

    x_intpol, y_intpol = catmull_rom(x, y, 100)

    out = Path()
    for i in range(len(x_intpol)):
        out.add(x_intpol[i], y_intpol[i])
    print(x_intpol)

    p = transform_path(out, out.bb(), ((0, 0), (dimensions[0] * 2, dimensions[1] * 2)))
    c = Collection()
    c.add(p)

    rr = RealtimeRenderer(dimensions[0] * 4, dimensions[1] * 4, "spline")
    rr.set_bg_color(arcade.color.WHITE)
    rr.add_collection(c, line_width=1, color=arcade.color.GRAY)

    rr.run()


import numpy
import matplotlib.pyplot as plt

QUADRUPLE_SIZE: int = 4

cole = None

def num_segments(point_chain: tuple) -> int:
    # There is 1 segment per 4 points, so we must subtract 3 from the number of points
    return len(point_chain) - (QUADRUPLE_SIZE - 1)


def flatten(list_of_lists) -> list:
    # E.g. mapping [[1, 2], [3], [4, 5]] to  [1, 2, 3, 4, 5]
    return [elem for lst in list_of_lists for elem in lst]


def catmull_rom_spline(
        P0: tuple,
        P1: tuple,
        P2: tuple,
        P3: tuple,
        num_points: int,
        alpha: float = 0.5,
):
    """
    Compute the points in the spline segment
    :param P0, P1, P2, and P3: The (x,y) point pairs that define the Catmull-Rom spline
    :param num_points: The number of points to include in the resulting curve segment
    :param alpha: 0.5 for the centripetal spline, 0.0 for the uniform spline, 1.0 for the chordal spline.
    :return: The points
    """

    # Calculate t0 to t4. Then only calculate points between P1 and P2.
    # Reshape linspace so that we can multiply by the points P0 to P3
    # and get a point for each value of t.
    def tj(ti: float, pi: tuple, pj: tuple) -> float:
        xi, yi = pi
        xj, yj = pj
        dx, dy = xj - xi, yj - yi
        l = (dx ** 2 + dy ** 2) ** 0.5
        return ti + l ** alpha

    t0: float = 0.0
    t1: float = tj(t0, P0, P1)
    t2: float = tj(t1, P1, P2)
    t3: float = tj(t2, P2, P3)
    t = numpy.linspace(t1, t2, num_points).reshape(num_points, 1)

    A1 = (t1 - t) / (t1 - t0) * P0 + (t - t0) / (t1 - t0) * P1
    A2 = (t2 - t) / (t2 - t1) * P1 + (t - t1) / (t2 - t1) * P2
    A3 = (t3 - t) / (t3 - t2) * P2 + (t - t2) / (t3 - t2) * P3
    B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
    B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3
    points = (t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2
    return points


def catmull_rom_chain(points: tuple, num_points: int) -> list:
    """
    Calculate Catmull-Rom for a sequence of initial points and return the combined curve.
    :param points: Base points from which the quadruples for the algorithm are taken
    :param num_points: The number of points to include in each curve segment
    :return: The chain of all points (points of all segments)
    """
    point_quadruples = (  # Prepare function inputs
        (points[idx_segment_start + d] for d in range(QUADRUPLE_SIZE))
        for idx_segment_start in range(num_segments(points))
    )
    all_splines = (catmull_rom_spline(*pq, num_points) for pq in point_quadruples)
    return flatten(all_splines)



def export_hpgl(rr: RealtimeRenderer = None):
    col = cole
    ExportWrapper().ex(
        col,
        PlotterType.ROLAND_DXY1200,
        PaperSize.LANDSCAPE_A4,
        20,
        "spline_test",
        f"VS42_{c.hash()}",
        keep_aspect_ratio=False,
    )


if __name__ == "__main__":
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 0.001)
    pa.add(0, 1)
    pa.add(1, 1)
    pa.add(1, 0)
    pa.add(0, 0)
    pa.add(0, 0.001)

    #POINTS: tuple = ((0, 1.5), (0, 1.5001), (2, 2), (3, 1), (4, 0.5), (5, 1), (6, 2), (7, 3), (7, 3.001))  # Red points
    NUM_POINTS: int = 10  # Density of blue chain points between two red points

    POINTS = tuple(pa.as_tuple_list())
    chain_points: list = catmull_rom_chain(POINTS, NUM_POINTS)
    assert len(chain_points) == num_segments(POINTS) * NUM_POINTS  # 400 blue points for this example

    out = Path()
    for poi in chain_points:
        pos = Position(poi[0], poi[1])
        out.add_position(pos)



    p = transform_path(out, out.bb(), ((0, 0), (dimensions[0] * 4, dimensions[1] * 4)))
    c = Collection()
    c.add(p)

    for i in range(42):
        _pa = p.parallel_offset(-10 * i)
        for __pa in _pa:
            __pa.velocity = 42 - i
        c.add(_pa)

    cole = c
    rr = RealtimeRenderer(dimensions[0] * 4, dimensions[1] * 4, "spline")
    rr.set_bg_color(arcade.color.WHITE)
    #rr.c = c
    rr.add_collection(c, line_width=2, color=arcade.color.GRAY)

    rr.add_cb(arcade.key.H, export_hpgl, False)

    rr.run()

    #plt.plot(*zip(*chain_points), c="blue")
    #plt.plot(*zip(*POINTS), c="red", linestyle="none", marker="o")
    #plt.show()

# if __name__ == '__main__':
#    test1()
