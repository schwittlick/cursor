from cursor.collection import Collection
from cursor.path import Path
from cursor.export import ExportWrapper
from cursor.device import PlotterType, PaperSize

if __name__ == "__main__":
    c = Collection()

    p = Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)

    p.velocity = 100

    c.add(p)

    ExportWrapper().ex(
        c,
        PlotterType.HP_7595A_A0,
        PaperSize.LANDSCAPE_A0,
        0,
        "simple_rect_example",
        "test",
    )
