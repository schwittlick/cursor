import numpy
import pytest

from cursor.hpgl.hpgl import HPGL
from cursor.hpgl.metrics import FontMetrics
from cursor.hpgl.parser import HPGLParser


def check_default_values(hpgl: HPGL) -> None:
    assert hpgl.plotter_unit == 40
    assert hpgl.pos == (0, 0)
    assert hpgl.metrics == FontMetrics(0.285, 0.375)
    assert hpgl.degree == 0
    assert hpgl.label_origin == 1


def test_IN():
    hpgl = HPGL()

    check_default_values(hpgl)
    assert hpgl.data == ""

    hpgl.IN()

    check_default_values(hpgl)
    assert hpgl.data == "IN;"


def test_SP():
    hpgl = HPGL()

    hpgl.SP(1)

    check_default_values(hpgl)
    assert hpgl.data == "SP1;"


def test_VS():
    hpgl = HPGL()

    hpgl.VS(110)

    check_default_values(hpgl)
    assert hpgl.data == "VS110;"


def test_DT():
    hpgl = HPGL()

    assert hpgl.terminator == chr(3)

    hpgl.DT(chr(66))

    check_default_values(hpgl)
    assert hpgl.terminator == chr(66)


def test_IW():
    hpgl = HPGL()

    hpgl.IW(1, 2, 3, 4)

    check_default_values(hpgl)
    assert hpgl.data == "IW1,2,3,4;"


def test_PA():
    hpgl = HPGL()

    hpgl.PA(12, 34)

    assert hpgl.pos == (12, 34)
    assert hpgl.data == "PA12,34;"


def test_PD():
    hpgl = HPGL()
    hpgl.PD(12, 34)
    assert hpgl.pos == (12, 34)
    assert hpgl.data == "PD12,34;"

    hpgl = HPGL()
    hpgl.PD()
    assert hpgl.pos == (0, 0)
    assert hpgl.data == "PD;"

    hpgl = HPGL()
    hpgl.PD(1)
    assert hpgl.pos == (0, 0)
    assert hpgl.data == "PD;"


def test_PU():
    hpgl = HPGL()
    hpgl.PU(12, 34)

    assert hpgl.pos == (12, 34)
    assert hpgl.data == "PU12,34;"

    hpgl = HPGL()
    hpgl.PU()
    assert hpgl.pos == (0, 0)
    assert hpgl.data == "PU;"

    hpgl = HPGL()
    hpgl.PU(1)
    assert hpgl.pos == (0, 0)
    assert hpgl.data == "PU;"


def test_SL():
    hpgl = HPGL()
    hpgl.SL(45)
    assert hpgl.data == "SL1.000;"

    hpgl = HPGL()
    hpgl.SL(-45)
    assert hpgl.data == "SL-1.000;"

    with pytest.raises(ValueError):
        hpgl.SL(90)

    with pytest.raises(ValueError):
        hpgl.SL(-90)


def test_DI():
    hpgl = HPGL()
    hpgl.DI(0)
    assert hpgl.data == "DI1.000,0.000;"

    hpgl = HPGL()
    hpgl.DI(45)
    assert hpgl.data == "DI0.707,0.707;"

    hpgl = HPGL()
    hpgl.DI(-45)
    assert hpgl.data == "DI0.707,-0.707;"


def test_SI():
    hpgl = HPGL()
    hpgl.SI(5, 5.1234)
    assert hpgl.data == "SI5.000,5.123;"
    assert hpgl.metrics.char_width_cm == 5
    assert hpgl.metrics.char_height_cm == 5.1234


def test_ES():
    hpgl = HPGL()
    hpgl.ES(1.2, 3.4)
    assert hpgl.data == "ES1.200,3.400;"
    hpgl.ES()
    assert hpgl.data == "ES1.200,3.400;ES0.000,0.000;"


def test_LO():
    hpgl = HPGL()
    hpgl.LO(2)
    assert hpgl.data == "LO2;"

    hpgl.LO()
    assert hpgl.data == "LO2;LO1;"

    with pytest.raises(ValueError):
        hpgl.LO(0)
    with pytest.raises(ValueError):
        hpgl.LO(10)
    with pytest.raises(ValueError):
        hpgl.LO(20)


def test_LB():
    hpgl = HPGL()
    hpgl.LB("Test")

    assert hpgl.data == f"LBTest{chr(3)}"

    # 4chars * default char size * 40 plotter units * 1.5 cell width
    assert hpgl.pos == pytest.approx((4 * 2.85 * 40 * 1.5, 0))


def test_LB_SI():
    hpgl = HPGL()
    hpgl.SI(2, 2)
    hpgl.LB("Test")

    assert hpgl.data == f"SI2.000,2.000;LBTest{chr(3)}"

    # 4chars * 10mm char size * 40 plotter units * 1.5 cell width
    assert hpgl.pos == pytest.approx((4 * 20 * 40 * 1.5, 0))

    hpgl = HPGL()
    hpgl.SI(-3, 2)
    hpgl.LB("Test")

    assert hpgl.data == f"SI-3.000,2.000;LBTest{chr(3)}"

    # 4chars * 10mm char size * 40 plotter units * 1.5 cell width
    assert hpgl.pos == pytest.approx((4 * -30 * 40 * 1.5, 0))


def test_LB_DI():
    hpgl = HPGL()
    hpgl.DI(45)
    hpgl.LB("Test")

    assert hpgl.data == f"DI0.707,0.707;LBTest{chr(3)}"

    # 4chars * 10mm char size * 40 plotter units * 1.5 char spacing
    # rotated by 45°
    assert numpy.allclose(hpgl.pos, (483.661, 483.661))


@pytest.mark.parametrize("degree", [0, 90, 180, 270])
@pytest.mark.parametrize("origin", [1, 5, 9, 11])
@pytest.mark.parametrize("extra_space", [0.0, -0.25, 0.5])
def test_LB_position_matches_what_the_parser_draws(degree, origin, extra_space):
    """
    The writer tracks the pen, the parser re-derives it. They must agree, or a plot and
    its preview drift apart the moment two labels follow each other.
    """
    hpgl = HPGL()
    hpgl.IN()
    hpgl.SP(1)
    hpgl.SI(1.0, 1.0)
    hpgl.ES(extra_space, 0)
    hpgl.DI(degree)
    hpgl.LO(origin)
    hpgl.PA(2000, 2000)
    hpgl.LB("Test")

    parser = HPGLParser()
    parser.parse(hpgl.data)

    assert parser.pos == pytest.approx(hpgl.pos, abs=1.0)


def test_LB_tracks_line_breaks():
    hpgl = HPGL()
    hpgl.SI(1.0, 1.0)

    hpgl.LB(f"ab{chr(13)}{chr(10)}cd")

    # CR returns to the starting column, LF drops one line height
    assert hpgl.pos == pytest.approx((2 * 600, -800))


def test_LO_sets_the_origin():
    hpgl = HPGL()
    hpgl.LO(9)

    assert hpgl.label_origin == 9

    hpgl.IN()
    assert hpgl.label_origin == 1
