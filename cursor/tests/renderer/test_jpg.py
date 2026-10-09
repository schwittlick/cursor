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


def white_pixels(renderer) -> int:
    rgb = renderer.img.convert("RGB")
    return sum(1 for x in range(rgb.width) if rgb.getpixel((x, 0)) == (255, 255, 255))


def test_drawing_after_render_reaches_the_image():
    """
    render() composites, which replaces the image object. The draw handle has to
    follow it, or anything drawn afterwards goes to an orphan and vanishes.
    """
    renderer = JpegRenderer(get_test_jpg_folder(), 64, 64)
    renderer.background((255, 255, 255))
    renderer.add(Path.from_tuple_list([(4, 4), (60, 60)]))
    renderer.render()

    assert white_pixels(renderer) == 64
    renderer.img_draw.rectangle((0, 0, 63, 63), outline=(255, 0, 0), width=1)
    assert white_pixels(renderer) == 0


def test_draw_handle_follows_a_rotate():
    renderer = JpegRenderer(get_test_jpg_folder(), 64, 32)
    renderer.background((255, 255, 255))
    renderer.rotate(90)

    assert renderer.img.width == 32
    renderer.img_draw.rectangle((0, 0, 31, 63), outline=(255, 0, 0), width=1)
    assert white_pixels(renderer) == 0
