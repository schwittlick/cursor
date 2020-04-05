from cursor.loader import Loader
from cursor.renderer import CursorSVGRenderer
from cursor.renderer import GCodeRenderer
from cursor.renderer import JpegRenderer
from cursor.data import DataDirHandler

import pytest


def test_svgrenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    vis = CursorSVGRenderer(DataDirHandler().test_svgs(), "test1")
    vis.render(rec)


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
    vis3 = CursorSVGRenderer(DataDirHandler().test_svgs(), "test1")

    rec = loader.all_collections()
    with pytest.raises(Exception):
        vis1.render(rec, "test1")

    with pytest.raises(Exception):
        vis2.render(rec, "test1")

    with pytest.raises(Exception):
        vis3.render(rec)
