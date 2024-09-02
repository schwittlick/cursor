from cursor.renderer.pdf import PdfRenderer
from cursor.tests.fixture import get_test_pdf_folder


def test_gcoderenderer():
    path = get_test_pdf_folder()
    r = PdfRenderer(path)
    r.pdf.add_page()
