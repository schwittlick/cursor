from cursor.device import Paper, PaperSize
from cursor.load.loader import Loader
from cursor.tests.fixture import get_test_recordings_path


def DISABLED_test_ascii_renderer():
    path = get_test_recordings_path()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    rec.fit(
        Paper.sizes[PaperSize.PORTRAIT_A3],
        padding_mm=0,
        cutoff_mm=0,
    )

    # r = JpegRenderer(DataDirHandler().test_images())
    # a = AsciiRenderer(DataDirHandler().test_ascii(), r)
    # a.render(rec, scale=1)
    # a.save("test1")
