from cursor.data import DataDirHandler
from cursor.loader import JsonCompressor
from cursor.path import Path
from cursor.collection import Collection


def test_experiments_path():
    custom_dir_gcode = DataDirHandler().gcode("custom")
    assert custom_dir_gcode.as_posix().endswith("cursor/data/experiments/custom/gcode")

    custom_dir_jpg = DataDirHandler().jpg("custom")
    assert custom_dir_jpg.as_posix().endswith("cursor/data/experiments/custom/jpg")

    custom_dir_svg = DataDirHandler().svg("custom")
    assert custom_dir_svg.as_posix().endswith("cursor/data/experiments/custom/svg")


def test_images_path():
    test_recordings_dir = DataDirHandler().images()
    assert test_recordings_dir.as_posix().endswith("cursor/data/jpg")


def test_gcode_path():
    test_recordings_dir = DataDirHandler().gcodes()
    assert test_recordings_dir.as_posix().endswith("cursor/data/gcode")


def test_svg_path():
    test_recordings_dir = DataDirHandler().svgs()
    assert test_recordings_dir.as_posix().endswith("cursor/data/svg")


def test_recordings_path():
    test_recordings_dir = DataDirHandler().recordings()
    assert test_recordings_dir.as_posix().endswith("cursor/data/recordings")


def test_test_images_path():
    test_recordings_dir = DataDirHandler().test_images()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/jpg")


def test_test_gcode_path():
    test_recordings_dir = DataDirHandler().test_gcodes()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/gcode")


def test_test_svg_path():
    test_recordings_dir = DataDirHandler().test_svgs()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/svg")


def test_test_recordings_path():
    test_recordings_dir = DataDirHandler().test_recordings()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/test_recordings")


def test_json_encoder():
    mouse_recordings = Collection()
    p1 = Path()
    p1.add(0, 0, 1626037613)
    mouse_recordings.add(p1)
    keyboard_recodings = []

    recs = {"mouse": mouse_recordings, "keys": keyboard_recodings}
    compressor = JsonCompressor()
    enc = compressor.json_zip(j=recs)
    assert 124 <= len(enc["base64(zip(o))"]) <= 142


def test_json_decoder():
    enc = "{'base64(zip(o))': 'eJyrVsrNLy1OVbJSqFYqSCzJKAayoqOrlSqAtIGOglIllC4BSR \
     iaGZkZGJubGRrXxsaCBDNzU4tLEnMLIHLmBiYWpuYGeoYGphYWRrVABdmplWADY2sB4yQcFQ=='}"
    compressor = JsonCompressor()
    res = compressor.json_unzip(eval(enc))
    assert len(res["mouse"]) == 1
    assert len(res["keys"]) == 0
