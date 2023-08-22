import pytest

from cursor.data import DataDirHandler
from cursor.device import PaperSize, Paper
from cursor.loader import Loader
from cursor.renderer.gcode import GCodeRenderer
from cursor.renderer.jpg import JpegRenderer
from cursor.renderer.svg import SvgRenderer


def test_jpegrenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.LANDSCAPE_A1],
        padding_mm=0,
        cutoff_mm=0,
    )

    r = JpegRenderer(DataDirHandler().test_images())
    r.render(rec)
    r.save("test1")


def test_jpegrenderer_size():
    renderer = JpegRenderer(DataDirHandler().test_images())
    assert renderer.image_width == 1920
    assert renderer.image_height == 1080

    renderer = JpegRenderer(DataDirHandler().test_images(), 4096, 4096)
    assert renderer.image_width == 4096
    assert renderer.image_height == 4096


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
