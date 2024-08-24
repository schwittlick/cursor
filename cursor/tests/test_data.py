from cursor.data import DataDirHandler


def test_experiments_path():
    custom_dir_gcode = DataDirHandler().gcode("custom")
    assert custom_dir_gcode.as_posix().endswith("cursor/data/experiments/custom/gcode")

    custom_dir_jpg = DataDirHandler().jpg("custom")
    assert custom_dir_jpg.as_posix().endswith("cursor/data/experiments/custom/jpg")

    custom_dir_svg = DataDirHandler().svg("custom")
    assert custom_dir_svg.as_posix().endswith("cursor/data/experiments/custom/svg")


def test_images_path():
    test_recordings_dir = DataDirHandler().jpgs()
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
