from cursor.loader import Loader
from cursor.renderer import SvgRenderer
from cursor.renderer import GCodeRenderer
from cursor.renderer import JpegRenderer
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

    vis = SvgRenderer(DataDirHandler().test_svgs(), "test1")
    vis.render(pc)


def test_gcoderenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    vis = GCodeRenderer(DataDirHandler().test_gcodes())
    vis.render(rec, "test1")


def test_jpegrenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    vis = JpegRenderer(DataDirHandler().test_images())
    vis.render(rec)
    vis.save("test1")


def test_jpegrenderer_fail():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    vis1 = JpegRenderer(DataDirHandler().test_images())
    vis2 = GCodeRenderer(DataDirHandler().test_gcodes())
    vis3 = SvgRenderer(DataDirHandler().test_svgs(), "test1")

    rec = loader.all_collections()
    with pytest.raises(Exception):
        vis1.render(rec, "test1")

    with pytest.raises(Exception):
        vis2.render(rec, "test1")

    with pytest.raises(Exception):
        vis3.render(rec)
