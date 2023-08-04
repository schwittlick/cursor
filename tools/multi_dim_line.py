import math

from cursor import misc
from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import PaperSize, Paper, XYFactors, PlotterType
from cursor.loader import Loader
from cursor.path import Path
from cursor.position import Position
from cursor.renderer import GCodeRenderer


def grid() -> Collection:
    width, height = 12, 10

    c = Collection()
    for y in range(height):
        for x in range(width):
            p = Path()
            z = y * 0.5
            delay = 0.5
            p.add_position(Position(x, y, properties={"z": z, "delay": delay}))
            p.add_position(Position(x, y, properties={"z": z}))
            p.properties["laser"] = True
            p.properties["amp"] = x * 0.005
            p.properties["volt"] = 3.3
            c.add(p)

    out_bb = Paper.sizes[PaperSize.PHOTO_PAPER_240_178_LANDSCAPE]
    c.transform(BoundingBox(10, 10, out_bb[0] - 10, out_bb[1] - 10))
    scale_fac = XYFactors.fac[PlotterType.DIY_PLOTTER]
    c.scale(scale_fac[0], scale_fac[1])
    return c


def cursor_sinelines() -> Collection:
    """
    get some random cursor lines
    and trace them with z-values from sine curve
    """
    recordings = DataDirHandler().recordings()
    _loader = Loader(directory=recordings, limit_files=3)
    paths = _loader.all_paths()

    c = Collection()

    count = 3

    for i in range(count):
        r1 = paths.random()
        r1_sin = sine_values(len(r1), 6, 6)
        for idx, p in enumerate(r1):
            p.properties["z"] = r1_sin[idx]

        r1.properties["laser"] = True
        r1.properties["amp"] = 0.01 * i
        r1.properties["volt"] = 3.3
        out_bb = Paper.sizes[PaperSize.PHOTO_PAPER_240_178_LANDSCAPE]
        r1.transform(r1.bb(), BoundingBox(10, 10, out_bb[0] - 10, out_bb[1] - 10))
        scale_fac = XYFactors.fac[PlotterType.DIY_PLOTTER]
        r1.scale(scale_fac[0], scale_fac[1])

        c.add(r1)

    return c


def sine_values(res, freq, amp) -> list[float]:
    values = []

    for i in range(res):
        v = misc.map(i, 0, res - 1, 0, math.pi * freq)
        v = math.sin(v) + 1.0
        v = v * amp / 2
        values.append(v)

    return values


def experiment1():
    """
    we use path for x, y
    properties will be z values and ampere values
    """
    path = Path()

    frequency = 2  # the times the sine cycles while going start -> end
    amplitude = 6
    resolution = 100
    start = (0, 100)
    end = (200, 100)

    values = []
    for i in range(resolution):
        v = misc.map(i, 0, resolution - 1, 0, math.pi * frequency)
        v = math.sin(v) + 1.0
        v = v * amplitude / 2
        values.append(v)

        x = misc.map(i, 0, resolution - 1, start[0], end[0])
        y = misc.map(i, 0, resolution - 1, start[1], end[1])

        pos = Position(x, y)
        pos.properties["z"] = v
        pos.properties["amp"] = 0.02
        pos.properties["volt"] = 3.3
        path.add_position(pos)

    path.properties["laser"] = True

    collection = Collection()
    collection.add(path)
    gcode_dir = DataDirHandler().gcode("multi-dim")
    gcode_renderer = GCodeRenderer(gcode_dir)
    gcode_renderer.render(collection)
    gcode_renderer.save("sine_line")
    # instructions = gcode_renderer.generate_instructions()
    # rr = RealtimeRenderer(1000, 1000, "multi-dim")
    # rr.add_path(path, line_width=1, color=arcade.color.BLACK)
    # rr.run()


if __name__ == "__main__":
    #c = cursor_sinelines()
    c = grid()
    gcode_dir = DataDirHandler().gcode("multi-dim")
    gcode_renderer = GCodeRenderer(gcode_dir)
    gcode_renderer.render(c)
    gcode_renderer.save("grid")
