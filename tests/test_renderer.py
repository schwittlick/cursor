from ..cursor.loader import Loader
from ..cursor.renderer import CursorSVGRenderer
from ..cursor.renderer import CursorGCodeRenderer
from ..cursor.renderer import JpegRenderer

from ..cursor.data import DataHandler

import os


def test_svgrenderer():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_collections()

    vis = CursorSVGRenderer(DataHandler.test_svgs())
    vis.render(rec, 'test1')


def test_gcoderenderer():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_collections()

    vis = CursorGCodeRenderer(DataHandler.test_gcodes())
    vis.render(rec, 'test1')


def test_jpegrenderer():
    path = DataHandler.test_recordings()
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_collections()

    vis = JpegRenderer(DataHandler.test_images())
    vis.render(rec, 'test1')