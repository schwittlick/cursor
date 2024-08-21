from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.renderer.gcode import GCodeRenderer
from cursor.renderer.pdf import PdfRenderer


def test_gcoderenderer():
    path = DataDirHandler().test_pdfs()
    r = PdfRenderer(path)
