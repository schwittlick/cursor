from cursor import device
from cursor import export
from cursor import path

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
        paths=pc,
        ptype=device.PlotterType.TEKTRONIX_4662,
        psize=device.PaperSize.LANDSCAPE_A3,
        margin=10,
        name="simple_rect_example",
        suffix="helloworld",
    )
