from cursor import collection
from cursor import export
from cursor import path
from cursor import device


if __name__ == "__main__":
    pc = collection.Collection()

    p = path.Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)
    pc.add(p)

    export.ExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A_A2,
        device.PaperSize.LANDSCAPE_A2,
        30,
        "simple_rect_example",
        "simple_rect",
    )
