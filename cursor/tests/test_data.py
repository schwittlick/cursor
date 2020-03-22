from cursor import data


def test_images_path():
    test_recordings_dir = data.DataHandler().images()
    assert test_recordings_dir.as_posix().endswith("cursor/data/jpgs")


def test_gcode_path():
    test_recordings_dir = data.DataHandler().gcodes()
    assert test_recordings_dir.as_posix().endswith("cursor/data/gcode")


def test_svg_path():
    test_recordings_dir = data.DataHandler().svgs()
    assert test_recordings_dir.as_posix().endswith("cursor/data/svg")


def test_recordings_path():
    test_recordings_dir = data.DataHandler().recordings()
    assert test_recordings_dir.as_posix().endswith("cursor/data/recordings")


def test_test_images_path():
    test_recordings_dir = data.DataHandler().test_images()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/jpgs")


def test_test_gcode_path():
    test_recordings_dir = data.DataHandler().test_gcodes()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/gcode")


def test_test_svg_path():
    test_recordings_dir = data.DataHandler().test_svgs()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/svg")


def test_test_recordings_path():
    test_recordings_dir = data.DataHandler().test_recordings()
    assert test_recordings_dir.as_posix().endswith("cursor/tests/data/test_recordings")
