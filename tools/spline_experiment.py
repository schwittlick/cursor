import arcade
import numpy as np

from cursor import misc
from cursor.collection import Collection
from cursor.device import Paper, PaperSize, PlotterType
from cursor.export import ExportWrapper
from cursor.position import Position
from cursor.renderer import RealtimeRenderer
from tools.spline import catmull_rom_chain, num_segments

np.set_printoptions(precision=4)

from cursor.path import Path

dimensions = Paper.sizes[PaperSize.LANDSCAPE_A4]


def export_hpgl(rr: RealtimeRenderer = None):
    ExportWrapper().ex(
        rr.collection,
        PlotterType.ROLAND_DXY1200,
        PaperSize.LANDSCAPE_A4,
        20,
        "spline_test",
        f"VS42_{c.hash()}",
        keep_aspect_ratio=False,
    )


def transform_path(path, bb, out):
    fn = misc.transformFn((bb.x, bb.y), (bb.x2, bb.y2), out[0], out[1])

    res = list(map(fn, path.generate))
    return Path.from_tuple_list(res)


if __name__ == "__main__":
    pa = Path()
    pa.add(0, 0)
    pa.add(0, 0.001)
    pa.add(0, 1)
    pa.add(1, 1)
    pa.add(1, 0)
    pa.add(0, 0)
    pa.add(0, 0.001)

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

    rr = RealtimeRenderer(dimensions[0] * 4, dimensions[1] * 4, "spline")
    rr.background(arcade.color.WHITE)
    rr.add_collection(c, line_width=2, color=arcade.color.GRAY)

    rr.add_cb(arcade.key.H, export_hpgl, False)

    rr.run()
