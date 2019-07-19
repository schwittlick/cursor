from loader import Loader
from renderer import CursorSVGRenderer
from renderer import CursorGCodeRenderer
from renderer import JpegRenderer

def test_svgrenderer():
    path = 'data/recordings/'
    loader = Loader(path=path)

    rec = loader.all()

    vis = CursorSVGRenderer()
    vis.render(rec, rec[0].resolution, 'test1')
    
def test_gcoderenderer():
    path = 'data/recordings/'
    loader = Loader(path=path)

    rec = loader.all()

    vis = CursorGCodeRenderer()
    vis.render(rec, 'test1')

def test_jpegrenderer():
    path = 'data/recordings/'
    loader = Loader(path=path)

    rec = loader.all()

    vis = JpegRenderer()
    vis.render(rec, rec[0].resolution, 'test1')