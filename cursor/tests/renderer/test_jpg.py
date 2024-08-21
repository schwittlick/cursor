from cursor.data import DataDirHandler
from cursor.device import PaperSize, Paper
from cursor.load.loader import Loader
from cursor.path import Path
from cursor.position import Position
from cursor.renderer.jpg import JpegRenderer


def test_new_api():
    renderer = JpegRenderer(DataDirHandler().test_images())
    renderer.add([Position(), Position()])
    renderer.add([Path(), Path()])


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
    r.add(rec)
    r.render()
    r.save("test1")


def test_jpegrenderer_size():
    renderer = JpegRenderer(DataDirHandler().test_images())
    assert renderer.img.width == 1920
    assert renderer.img.height == 1080

    renderer = JpegRenderer(DataDirHandler().test_images(), 4096, 4096)
    assert renderer.img.width == 4096
    assert renderer.img.height == 4096
