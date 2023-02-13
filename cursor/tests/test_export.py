from cursor.collection import Collection
from cursor.device import PlotterType, PaperSize
from cursor.export import ExportWrapper
from cursor.path import Path


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

    ExportWrapper().ex(
        pc,
        PlotterType.HP_7470A,
        PaperSize.LANDSCAPE_A4,
        25,
        "test",
        "111",
        keep_aspect_ratio=False,
    )
