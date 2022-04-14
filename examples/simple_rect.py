from cursor import device
from cursor import export
from cursor import path


if __name__ == "__main__":
    pc = path.PathCollection()

    p = path.Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)
    pc.add(p)

    export.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300_A3,
        device.PaperSize.LANDSCAPE_A3,
        10,
        "simple_rect_example",
        "simple_rect",
    )
