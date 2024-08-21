from cursor.data import DataDirHandler
from cursor.renderer.pdf import PdfRenderer


def test_gcoderenderer():
    path = DataDirHandler().test_pdfs()
    r = PdfRenderer(path)
    r.pdf.add_page()
