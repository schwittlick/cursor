from cursor.data import DataDirHandler


def test_experiments_path():
    custom_dir_gcode = DataDirHandler().gcode("custom")
    gcode_parts = custom_dir_gcode.parts
    assert gcode_parts[-3:] == ("experiments", "custom", "gcode")

    custom_dir_jpg = DataDirHandler().jpg("custom")
    jpg_parts = custom_dir_jpg.parts
    assert jpg_parts[-3:] == ("experiments", "custom", "jpg")

    custom_dir_svg = DataDirHandler().svg("custom")
    svg_parts = custom_dir_svg.parts
    assert svg_parts[-3:] == ("experiments", "custom", "svg")


def test_images_path():
    images_dir = DataDirHandler().jpgs()
    assert images_dir.parts[-1:] == ("jpg",)


def test_gcode_path():
    gcode_dir = DataDirHandler().gcodes()
    assert gcode_dir.parts[-1:] == ("gcode",)


def test_svg_path():
    svg_dir = DataDirHandler().svgs()
    assert svg_dir.parts[-1:] == ("svg",)


def test_recordings_path():
    recordings_dir = DataDirHandler().recordings()
    assert recordings_dir.parts[-1:] == ("recordings",)


def test_test_images_path():
    test_images_dir = DataDirHandler().test_images()
    assert test_images_dir.parts[-4:] == ("cursor", "tests", "data", "jpg")


def test_test_gcode_path():
    test_gcode_dir = DataDirHandler().test_gcodes()
    assert test_gcode_dir.parts[-4:] == ("cursor", "tests", "data", "gcode")


def test_test_svg_path():
    test_svg_dir = DataDirHandler().test_svgs()
    assert test_svg_dir.parts[-4:] == ("cursor", "tests", "data", "svg")


def test_test_recordings_path():
    test_recordings_dir = DataDirHandler().test_recordings()
    assert test_recordings_dir.parts[-4:] == ("cursor", "tests", "data", "test_recordings")
