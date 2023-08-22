from cursor.data import DataDirHandler
from cursor.device import Paper, PaperSize
from cursor.loader import Loader
from cursor.renderer.ascii import AsciiRenderer
from cursor.renderer.jpg import JpegRenderer


def test_ascii_renderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.PORTRAIT_A3],
        padding_mm=0,
        cutoff_mm=0,
    )

    r = JpegRenderer(DataDirHandler().test_images())
    a = AsciiRenderer(DataDirHandler().test_ascii(), r)
    a.render(rec, scale=1, thickness=30)
    a.save("test1")
