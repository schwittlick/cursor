import logging

from cursor.data import DataDirHandler
from cursor.hpgl.analyze import HPGLAnalyzer, Pen, PenData


def test_analyze():
    analyzer = HPGLAnalyzer()
    file = DataDirHandler().test_hpgls() / "complex_hpgl01.hpgl"
    data = analyzer.analyze(file)

    assert data.total_pen_up == 545
    assert data.total_pen_down == 0
    assert data.total_number_of_dots == 5872

    data_per_pen = {
        Pen(1): PenData(0, 69, 1412),
        Pen(2): PenData(0, 129, 2384),
        Pen(3): PenData(0, 7, 428),
        Pen(4): PenData(0, 59, 1056),
        Pen(5): PenData(0, 0, 2),
        Pen(6): PenData(0, 0, 2),
        Pen(7): PenData(0, 12, 552),
        Pen(8): PenData(0, 0, 36),
    }

    assert data.data_per_pen == data_per_pen
