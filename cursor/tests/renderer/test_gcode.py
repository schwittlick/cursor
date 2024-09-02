from cursor.load.loader import Loader
from cursor.renderer.gcode import GCodeRenderer
from cursor.tests.fixture import get_test_recordings_path, get_test_gcode_folder


def test_gcoderenderer():
    path = get_test_recordings_path()
    loader = Loader(directory=path)

    rec = loader.all_paths()

    r = GCodeRenderer(get_test_gcode_folder())
    r.render(rec)
    r.save("test1")
