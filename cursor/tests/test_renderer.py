from cursor.loader import Loader
from cursor.renderer import SvgRenderer
from cursor.renderer import GCodeRenderer
from cursor.renderer import JpegRenderer
from cursor.renderer import HPGLRenderer
from cursor.renderer import PathIterator
from cursor.data import DataDirHandler
from cursor.path import PathCollection
from cursor.path import Path

import pytest


def test_pathiterator():
    pc = PathCollection()
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p2 = Path()
    p2.add(0, 1)
    p2.add(1, 1)
    p2.add(1, -1)

    pc.add(p1)
    pc.add(p2)

    pi = PathIterator(pc)
    sum_p = sum(1 for _ in pi.points())
    assert sum_p == 5

    sum_c = sum(1 for _ in pi.connections())
    assert sum_c == 3


def test_pathiterator2():
    pc = PathCollection()
    p1 = Path()
    p1.add(0, 0)
    p2 = Path()
    p2.add(0, 1)
    p2.add(1, 1)
    p2.add(1, -1)

    pc.add(p1)
    pc.add(p2)

    pi = PathIterator(pc)
    sum_p = sum(1 for _ in pi.points())
    assert sum_p == 4

    sum_c = sum(1 for _ in pi.connections())
    assert sum_c == 2


def test_svgrenderer():
    pc = PathCollection()
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p2 = Path()
    p2.add(0, 1)
    p2.add(1, 1)

    pc.add(p1)
    pc.add(p2)

    r = SvgRenderer(DataDirHandler().test_svgs())
    r.render(pc)
    r.save("test1")


def test_gcoderenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    r = GCodeRenderer(DataDirHandler().test_gcodes())
    r.render(rec)
    r.save("test1")


def test_jpegrenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    r = JpegRenderer(DataDirHandler().test_images())
    r.render(rec)
    r.save("test1")


def test_hpglrenderer():
    pc = PathCollection()
    p1 = Path()
    p1.add(-10000, -10000)
    p1.add(10000, -10000)
    p2 = Path()
    p2.add(10000, -10000)
    p2.add(10000, 10000)

    p3 = Path()
    p3.add(10000, 10000)
    p3.add(-10000, 10000)

    p4 = Path()
    p4.add(-10000, 10000)
    p4.add(-10000, -10000)

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)

    r = HPGLRenderer(DataDirHandler().test_hpgls())
    r.render(pc)
    r.save("test1")


def test_jpegrenderer_fail():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    jpeg_r = JpegRenderer(DataDirHandler().test_images())
    gcode_r = GCodeRenderer(DataDirHandler().test_gcodes())
    svg_r = SvgRenderer(DataDirHandler().test_svgs())

    rec = loader.all_collections()
    with pytest.raises(Exception):
        jpeg_r.render(rec)
        jpeg_r.save("test1")

    with pytest.raises(Exception):
        gcode_r.render(rec)
        gcode_r.save("test1")

    with pytest.raises(Exception):
        svg_r.render(rec)
        svg_r.save("test1")


def test_tsp():
    p0 = Path()
    p0.add(0, 0)
    p0.add(1, 0)
    p0.add(2, 0)
    p0.add(3, 0)
    p0.add(4, 0)

    p1 = Path()
    p1.add(2, 2)
    p1.add(2, 3)
    p1.add(2, 4)
    p1.add(2, 5)
    p1.add(2, 6)

    p2 = Path()
    p2.add(20, 20)
    p2.add(25, 20)
    p2.add(27, 20)
    p2.add(30, 20)
    p2.add(40, 20)

    p3 = Path()
    p3.add(50, 50)
    p3.add(50, 60)
    p3.add(50, 70)
    p3.add(50, 80)
    p3.add(50, 90)
    p3.add(100, 100)

    p4 = Path()
    p4.add(1, 0)
    p4.add(3, 3)
    p4.add(4, 4)
    p4.add(5, 5)
    p4.add(1, 0)

    pc = PathCollection()
    pc.add(p0)
    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)

    pc.optimize_order()

    assert pc[0] == p4
    assert pc[1] == p0
    assert pc[2] == p1
    assert pc[3] == p3
    assert pc[4] == p2