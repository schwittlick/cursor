from ..cursor.loader import Loader
from ..cursor.renderer import CursorSVGRenderer
from ..cursor.renderer import CursorGCodeRenderer
from ..cursor.renderer import JpegRenderer

from ..cursor.data import DataHandler

import os
import pytest


def test_svgrenderer():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_paths()

    vis = CursorSVGRenderer(DataHandler.test_svgs())
    vis.render(rec, 'test1')


def test_gcoderenderer():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_paths()

    vis = CursorGCodeRenderer(DataHandler.test_gcodes())
    vis.render(rec, 'test1')


def test_jpegrenderer():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_paths()

    vis = JpegRenderer(DataHandler.test_images())
    vis.render(rec, 'test1')

def test_jpegrenderer_fail():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    vis1 = JpegRenderer(DataHandler.test_images())
    vis2 = CursorGCodeRenderer(DataHandler.test_gcodes())
    vis3 = CursorSVGRenderer(DataHandler.test_svgs())

    rec = loader.all_collections()
    with pytest.raises(Exception):
        vis1.render(rec, 'test1')

    with pytest.raises(Exception):
        vis2.render(rec, 'test1')

    with pytest.raises(Exception):
        vis3.render(rec, 'test1')