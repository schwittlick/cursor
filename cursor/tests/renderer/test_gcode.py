from cursor.data import DataDirHandler
from cursor.load.loader import Loader
from cursor.renderer.gcode import GCodeRenderer


def test_gcoderenderer():
    path = DataDirHandler().test_recordings()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    r = GCodeRenderer(DataDirHandler().test_gcodes())
    r.render(rec)
    r.save("test1")
