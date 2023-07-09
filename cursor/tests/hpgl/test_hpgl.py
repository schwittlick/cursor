import pytest

from cursor.hpgl.hpgl import HPGL


def check_default_values(hpgl: HPGL) -> None:
    assert hpgl.plotter_unit == 40
    assert hpgl.pos == (0, 0)
    assert hpgl.char_size_mm == (10, 10)
    assert hpgl.char_spacing == 1.5
    assert hpgl.line_spacing == 2.0
    assert hpgl.degree == 0
    assert hpgl.direction_vertical == 0


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


def test_DV():
    hpgl = HPGL()
    hpgl.DV(1)
    assert hpgl.data == "DV1;"

    with pytest.raises(ValueError):
        hpgl.DV(-1)
    with pytest.raises(ValueError):
        hpgl.DV(2)


def test_SI():
    hpgl = HPGL()
    hpgl.SI(5, 5.1234)
    assert hpgl.data == "SI5.000,5.123;"
    assert hpgl.char_size_mm == (50, 51.234)


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

    # 4chars * 10mm * 40 plotter units * 1.5 char spacing
    assert hpgl.pos == (4 * 400 * 1.5, 0)


def test_LB_SI():
    hpgl = HPGL()
    hpgl.SI(2, 2)
    hpgl.LB("Test")

    assert hpgl.data == f"SI2.000,2.000;LBTest{chr(3)}"

    # 4chars * 10mm char size * 40 plotter units * 1.5 char spacing
    assert hpgl.pos == (4 * 20 * 40 * 1.5, 0)

    hpgl = HPGL()
    hpgl.SI(-3, 2)
    hpgl.LB("Test")

    assert hpgl.data == f"SI-3.000,2.000;LBTest{chr(3)}"

    # 4chars * 10mm char size * 40 plotter units * 1.5 char spacing
    assert hpgl.pos == (4 * -30 * 40 * 1.5, 0)


def test_LB_DI():
    hpgl = HPGL()
    hpgl.DI(45)
    hpgl.LB("Test")

    assert hpgl.data == f"DI0.707,0.707;LBTest{chr(3)}"

    # 4chars * 10mm char size * 40 plotter units * 1.5 char spacing
    # rotated by 45°
    assert hpgl.pos == (1697.0562748477141, 1697.0562748477141)


def test_LB_DV():
    hpgl = HPGL()
    hpgl.DV(1)
    hpgl.LB("Test")

    assert hpgl.data == f"DV1;LBTest{chr(3)}"

    # to the right: 1chars * 10mm char size * 40 plotter units * 1.5 char spacing
    # to the bottom: 4 chars * 10mm char size * 40 plotter units * 2 line spacing
    assert hpgl.pos == (10 * 40 * 1.5, 4 * 10 * 40 * 2.0)


def test_LB_DI_DV():
    hpgl = HPGL()
    hpgl.DI(45)
    hpgl.DV(1)
    hpgl.LB("Test")

    assert hpgl.data == f"DI0.707,0.707;DV1;LBTest{chr(3)}"

    # to the right: 1chars * 10mm char size * 40 plotter units * 1.5 char spacing
    # to the bottom: 4 chars * 10mm char size * 40 plotter units * 2 line spacing
    # rotated by 45°
    assert hpgl.pos == (10 * 40 * 1.5, 4 * 10 * 40 * 2.0)
