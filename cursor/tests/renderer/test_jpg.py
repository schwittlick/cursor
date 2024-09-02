from cursor.device import PaperSize, Paper
from cursor.load.loader import Loader
from cursor.path import Path
from cursor.position import Position
from cursor.renderer.jpg import JpegRenderer
from cursor.tests.fixture import get_test_recordings_path, get_test_jpg_folder


def test_new_api():
    renderer = JpegRenderer(get_test_jpg_folder())
    renderer.add([Position(), Position()])
    renderer.add([Path(), Path()])


def test_jpegrenderer():
    path = get_test_recordings_path()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.LANDSCAPE_A1],
        padding_mm=0,
        cutoff_mm=0,
    )

    r = JpegRenderer(get_test_jpg_folder())
    r.add(rec)
    r.render()
    r.save("test1")


def test_jpegrenderer_size():
    renderer = JpegRenderer(get_test_jpg_folder())
    assert renderer.img.width == 1920
    assert renderer.img.height == 1080

    renderer = JpegRenderer(get_test_jpg_folder(), 4096, 4096)
    assert renderer.img.width == 4096
    assert renderer.img.height == 4096
