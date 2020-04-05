from cursor import data


def test_experiments_path():
    custom_dir_gcode = data.DataDirHandler().gcode("custom")
    assert custom_dir_gcode.as_posix().endswith("cursor/data/experiments/custom/gcode")

    custom_dir_jpg = data.DataDirHandler().jpg("custom")
    assert custom_dir_jpg.as_posix().endswith("cursor/data/experiments/custom/jpg")

    custom_dir_svg = data.DataDirHandler().svg("custom")
    assert custom_dir_svg.as_posix().endswith("cursor/data/experiments/custom/svg")


def test_images_path():
    test_recordings_dir = data.DataDirHandler().images()
    assert test_recordings_dir.as_posix().endswith("cursor/data/jpgs")


def test_gcode_path():
    test_recordings_dir = data.DataDirHandler().gcodes()
    assert test_recordings_dir.as_posix().endswith("cursor/data/gcode")


def test_svg_path():
    test_recordings_dir = data.DataDirHandler().svgs()
    assert test_recordings_dir.as_posix().endswith("cursor/data/svg")


def test_recordings_path():
    test_recordings_dir = data.DataDirHandler().recordings()
    assert test_recordings_dir.as_posix().endswith("cursor/data/recordings")


def test_test_images_path():
    test_recordings_dir = data.DataDirHandler().test_images()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/jpgs")


def test_test_gcode_path():
    test_recordings_dir = data.DataDirHandler().test_gcodes()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/gcode")


def test_test_svg_path():
    test_recordings_dir = data.DataDirHandler().test_svgs()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/svg")


def test_test_recordings_path():
    test_recordings_dir = data.DataDirHandler().test_recordings()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/test_recordings")
