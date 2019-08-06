from ..cursor.loader import Loader
from ..cursor.renderer import CursorSVGRenderer
from ..cursor.renderer import CursorGCodeRenderer
from ..cursor.renderer import JpegRenderer

import os


def test_svgrenderer():
    path = 'data/test_recordings/'
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_collections()

    vis = CursorSVGRenderer()
    vis.render(rec, rec[0].resolution, 'test1')


def test_gcoderenderer():
    path = 'data/test_recordings/'
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_collections()

    vis = CursorGCodeRenderer()
    vis.render(rec, 'test1')


def test_jpegrenderer():
    path = 'data/test_recordings/'
    loader = Loader(directory=os.path.abspath(path))

    rec = loader.all_collections()

    vis = JpegRenderer()
    vis.render(rec, rec[0].bb(), 'test1')