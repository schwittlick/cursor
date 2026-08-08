import math
import pathlib

import pytest

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.hpgl.parser import HPGLParser
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


def test_hpgl_parser_PAPD():
    paths = HPGLParser().parse("IN;SP1;PA100,0;PD100,100;PU;PA0,0;")

    path = Path.from_tuple_list([(100, 0.0), (100, 100.0)])
    path.pen_select = 1

    collection = Collection.from_path_list([path])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_LB():
    paths = HPGLParser().parse("IN;SP1;LBHI")

    properties = {Property.PEN_SELECT: 1, "label": 1}

    path1 = Path([Position(0.0, 150.0), Position(0.0, 0.0)], properties)
    path2 = Path([Position(114.0, 150.0), Position(114.0, 0.0)], properties)
    path3 = Path([Position(0.0, 79.6875), Position(114.0, 79.6875)], properties)
    path4 = Path([Position(185.25, 150.0), Position(270.75, 150.0)], properties)
    path5 = Path([Position(228.0, 150.0), Position(228.0, 0.0)], properties)
    path6 = Path([Position(185.25, 0.0), Position(270.75, 0.0)], properties)
    collection = Collection.from_path_list([path1, path2, path3, path4, path5, path6])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_DI():
    paths = HPGLParser().parse("IN;SP1;DI0,1;PA100,0;PD100,100;")

    path = Path.from_tuple_list([(100, 0.0), (100, 100.0)])
    path.pen_select = 1
    collection = Collection()
    collection.add(path)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string():
    parser = HPGLParser()
    paths = parser.parse("IN;SP1;SI1,1;PA100,0;LB1")

    properties = {Property.PEN_SELECT: 1, "label": 1}

    path1 = Path([Position(200.0, 0.0), Position(450.0, 0.0)], properties)
    path2 = Path(
        [Position(200.0, 250.0), Position(350.0, 400.0), Position(350.0, 0.0)],
        properties,
    )
    collection = Collection.from_path_list([path1, path2])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_string2():
    string = (
        "SP1;SI1.000,1.000;DI0.839,0.545;LBTDI1.000,0.000;SP3;LBAIN;PU0,0;SP4;SI1.000,1.000;DI0.839,"
        "0.545;LBASP2;PA201,130;PD1201,1130;"
    )
    parser = HPGLParser()
    paths = parser.parse(string)

    properties = {Property.PEN_SELECT: 1, "label": 1}

    path1 = Path([Position(-217.8970, 335.4414), Position(117.5444, 553.3383)], properties)
    path2 = Path([Position(-50.1763, 444.3899), Position(167.7207, 108.9485)], properties)
    # these two follow the "T" plotted at DI0.839,0.545, so they start one character cell
    # away from the origin along that direction: 600 units at 33.0 degrees
    path3 = Path(
        [
            Position(503.1621, 326.8454),
            Position(703.1621, 726.8454),
            Position(903.1621, 326.8454),
        ],
        {Property.PEN_SELECT: 3, "label": 3},
    )
    path4 = Path(
        [Position(553.1621, 426.8454), Position(853.1621, 426.8454)],
        {Property.PEN_SELECT: 3, "label": 3},
    )
    path5 = Path(
        [
            Position(0.0, 0.0),
            Position(-50.1763, 444.3899),
            Position(335.4414, 217.8970),
        ],
        {Property.PEN_SELECT: 4, "label": 4},
    )
    path6 = Path(
        [Position(-12.5441, 111.0975), Position(239.0370, 274.5202)],
        {Property.PEN_SELECT: 4, "label": 4},
    )
    path7 = Path([Position(201.0, 130.0), Position(1201.0, 1130.0)], {Property.PEN_SELECT: 2})

    collection = Collection.from_path_list([path1, path2, path3, path4, path5, path6, path7])

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def test_hpgl_parser_PA():
    test_data_path = pathlib.Path(__file__).resolve().parent.parent / "data"
    file = test_data_path / "hpgl_pa_pd_pu.hpgl"
    parser = HPGLParser()
    paths = parser.parse(file)

    path = Path.from_tuple_list([(100, 0), (100, 100)])
    path.pen_select = 1

    collection = Collection()
    collection.add(path)

    assert len(paths) == len(collection)

    for i in range(len(paths)):
        assert paths[i] == collection[i]


def _label_bb(hpgl_string: str) -> BoundingBox:
    return HPGLParser().parse(hpgl_string).bb()


def test_parser_advances_along_the_di_direction():
    """The pen must move one cell width along DI, whatever quadrant that lands in."""
    for degrees, (run, rise) in {
        0: (1.0, 0.0),
        33: (0.839, 0.545),
        90: (0.0, 1.0),
        180: (-1.0, 0.0),
        270: (-0.0, -1.0),
    }.items():
        parser = HPGLParser()
        parser.parse(f"SP1;SI1.000,1.000;DI{run:.3f},{rise:.3f};PA0,0;LBA{chr(3)}")

        x, y = parser.pos
        assert math.hypot(x, y) == pytest.approx(600, abs=0.5)

        off_by = (math.degrees(math.atan2(y, x)) - degrees) % 360
        assert min(off_by, 360 - off_by) == pytest.approx(0, abs=0.1)


def test_parser_rotates_glyphs_in_every_quadrant():
    """A rotated glyph keeps its size but swaps which way it extends from the anchor."""
    upright = _label_bb(f"SP1;SI1.000,1.000;DI1.000,0.000;PA1000,1000;LBL{chr(3)}")
    assert upright.x >= 1000 and upright.y >= 1000

    half_turn = _label_bb(f"SP1;SI1.000,1.000;DI-1.000,0.000;PA1000,1000;LBL{chr(3)}")
    assert half_turn.x2 <= 1000 and half_turn.y2 <= 1000
    assert half_turn.w == pytest.approx(upright.w)
    assert half_turn.h == pytest.approx(upright.h)

    quarter = _label_bb(f"SP1;SI1.000,1.000;DI0.000,1.000;PA1000,1000;LBL{chr(3)}")
    assert quarter.x2 <= 1000 and quarter.y >= 1000

    three_quarter = _label_bb(f"SP1;SI1.000,1.000;DI-0.000,-1.000;PA1000,1000;LBL{chr(3)}")
    assert three_quarter.x >= 1000 and three_quarter.y2 <= 1000


def test_parser_label_origin_shifts_the_label():
    """LO moves the label off the point, LO1 being the default of bottom left."""
    default = _label_bb(f"SP1;SI1.000,1.000;PA2000,2000;LBAB{chr(3)}")
    left_bottom = _label_bb(f"SP1;SI1.000,1.000;LO1;PA2000,2000;LBAB{chr(3)}")
    assert left_bottom.x == pytest.approx(default.x)
    assert left_bottom.y == pytest.approx(default.y)

    right_top = _label_bb(f"SP1;SI1.000,1.000;LO9;PA2000,2000;LBAB{chr(3)}")
    assert right_top.x2 < 2000 and right_top.y2 <= 2000
    assert right_top.w == pytest.approx(default.w)

    centered = _label_bb(f"SP1;SI1.000,1.000;LO5;PA2000,2000;LBAB{chr(3)}")
    assert (centered.x + centered.x2) / 2 == pytest.approx(2000, abs=default.w / 2)


def test_parser_label_origin_survives_rotation():
    """The origin offset is in the text's frame, so it turns with DI."""
    upright = _label_bb(f"SP1;SI1.000,1.000;LO7;PA2000,2000;LBAB{chr(3)}")
    turned = _label_bb(f"SP1;SI1.000,1.000;DI0.000,1.000;LO7;PA2000,2000;LBAB{chr(3)}")

    # right-aligned text ends at the point, so turning it a quarter turn hangs it below
    # the point by exactly what it reached back from the point when upright
    assert 2000 - turned.y2 == pytest.approx(2000 - upright.x2)
    assert 2000 - turned.y == pytest.approx(2000 - upright.x)


def test_parser_handles_line_breaks_within_a_label():
    """CR returns to the label's column, LF drops a line."""
    single = _label_bb(f"SP1;SI1.000,1.000;PA0,0;LBAB{chr(3)}")
    broken = _label_bb(f"SP1;SI1.000,1.000;PA0,0;LBA{chr(13)}{chr(10)}B{chr(3)}")

    assert broken.w < single.w
    assert broken.h > single.h
