import pathlib


def get_test_recordings_path():
    return pathlib.Path(__file__).resolve().parent / "data" / "test_recordings"


def get_test_hpgl_folder():
    return pathlib.Path(__file__).resolve().parent / "data" / "hpgl"


def get_test_gcode_folder():
    return pathlib.Path(__file__).resolve().parent / "data" / "gcode"


def get_test_jpg_folder():
    return pathlib.Path(__file__).resolve().parent / "data" / "jpg"


def get_test_pdf_folder():
    return pathlib.Path(__file__).resolve().parent / "data" / "pdf"


def get_test_svg_folder():
    return pathlib.Path(__file__).resolve().parent / "data" / "svg"
