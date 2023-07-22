from cursor.collection import Collection
from cursor.path import Path
from cursor.export import ExportWrapper
from cursor.device import PlotterType, PaperSize

if __name__ == "__main__":
    c = Collection()

    p = Path.from_tuple_list([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])

    p.velocity = 100

    c.add(p)

    ExportWrapper().ex(
        c,
        PlotterType.ROLAND_DXY1200,
        PaperSize.PHOTO_PAPER_240_178_LANDSCAPE,
        10,
        "simple_rect_example",
        "test",
    )
