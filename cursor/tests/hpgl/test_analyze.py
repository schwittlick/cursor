from cursor.data import DataDirHandler
from cursor.hpgl.analyze import HPGLAnalyzer, Pen, PenData, HPGLAnalyzeData


def test_analyze():
    analyzer = HPGLAnalyzer()
    file = DataDirHandler().test_hpgls() / "complex_hpgl01.hpgl"
    data = analyzer.analyze(file)

    analyzed_data_to_compare = HPGLAnalyzeData(545, 0, 5872, 68)

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
    analyzed_data_to_compare.data_per_pen = data_per_pen

    assert data == analyzed_data_to_compare
