from cursor.loader import Loader
from cursor.device import Paper
from cursor.device import PaperSize
from cursor.renderer import SvgRenderer
from cursor.renderer import GCodeRenderer
from cursor.renderer import JpegRenderer
from cursor.renderer import HPGLRenderer
from cursor.renderer import AsciiRenderer
from cursor.renderer import PathIterator
from cursor.renderer import TektronixRenderer
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

    rec.fit(
        Paper.sizes[PaperSize.LANDSCAPE_A1], padding_mm=0, cutoff_mm=0,
    )

    r = JpegRenderer(DataDirHandler().test_images())
    r.render(rec)
    r.save("test1")


def test_hpglrenderer():
    pc = PathCollection()
    p1 = Path()
    p1.add(-10, -10)
    p1.add(10, -10)

    p2 = Path()
    p2.add(10, -10)
    p2.add(10, 10)

    pc.add(p1)
    pc.add(p2)

    r = HPGLRenderer(DataDirHandler().test_hpgls())
    r.render(pc)
    hpgl_data = r.save("test1")

    expected_result = (
        "SP1;\n"
        "PA0,0\n"
        "PU;\n"
        "SP1;\n"
        "LT;\n"
        "VS110;\n"
        "FS16;\n"
        "PA-10,-10;\n"
        "PD;\n"
        "PA-10,-10;\n"
        "PA10,-10;\n"
        "PU;\n"
        "SP1;\n"
        "LT;\n"
        "VS110;\n"
        "FS16;\n"
        "PA10,-10;\n"
        "PD;\n"
        "PA10,-10;\n"
        "PA10,10;\n"
        "PU;\n"
        "PA0,0\n"
        "SP0;\n"
    )
    assert hpgl_data == expected_result


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


@pytest.mark.skip(reason="This takes too long to run.")
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

    pc.reorder_tsp()

    assert pc[0] == p4
    assert pc[1] == p0
    assert pc[2] == p1
    assert pc[3] == p3
    assert pc[4] == p2


def test_reorder_custom():
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

    pc.reorder_quadrants(3, 3)

    assert pc[0] == p0
    assert pc[1] == p1
    assert pc[2] == p2
    assert pc[3] == p3
    assert pc[4] == p4


def test_ascii_renderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.PORTRAIT_A3], padding_mm=0, cutoff_mm=0,
    )

    r = JpegRenderer(DataDirHandler().test_images())
    a = AsciiRenderer(DataDirHandler().test_ascii(), r)
    a.render(rec, scale=1, thickness=30)
    a.save("test1")


def test_tektronix_renderer():
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

    pc = PathCollection()
    pc.add(p0)
    pc.add(p1)

    renderer = TektronixRenderer(DataDirHandler().test_hpgls())
    renderer.render(pc)
    out = renderer.save("tektronix_test01")

    assert out == 'AE `` @ `` @ a` @ b` @ c` @ `` A j` @ j` @ n` @ ba @ fa @ ja @ `` @'


def disabled_test_pdf_renderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.PORTRAIT_A4], padding_mm=0, cutoff_mm=0,
    )

    r = JpegRenderer(DataDirHandler().test_images())
    a = AsciiRenderer(DataDirHandler().test_ascii(), r)
    a.render(rec, scale=1, thickness=30)

    text = a.output.splitlines()

    import fpdf

    pdf = fpdf.FPDF(orientation="L", unit="mm", format="A4")

    fontpath = DataDirHandler().test_data_file("JetBrainsMono-Regular.ttf")
    pdf.add_font(
        "JetbrainsMono", "", fontpath, uni=True,
    )
    pdf.add_page()
    pdf.set_margins(0, 0)
    pdf.set_font("JetbrainsMono", size=14)
    linecounter = 0
    for line in text:
        # pdf.cell(0, 3, txt=line, ln=1, align="L")
        pdf.text(0, linecounter * 6 + 5, line)
        linecounter += 1

    out = DataDirHandler().test_data_dir / "simple_demo.pdf"
    pdf.output(out)
