from cursor.collection import Collection
from cursor.device import PlotterType
from cursor.export import ExportWrapper, Exporter
from cursor.path import Path


def test_filename():
    fn = Exporter._file_content_of_caller()
    print(fn)


def test_simple_export():
    p = Path()
    p.add(3, 5)
    p.add(5, 9)
    p.add(3, 10)
    p.pen_select = 1

    p2 = Path()
    p2.add(1, 6)
    p2.add(3, 5)
    p2.add(3, 8)
    p2.pen_select = 2

    pc = Collection()
    pc.add(p)
    pc.add(p2)

    wrapper = ExportWrapper(
        pc,
        PlotterType.HP_7470A_A4,
        25,
        "test",
        "111",
        keep_aspect_ratio=False,
    )

    wrapper.fit()
    wrapper.ex()
