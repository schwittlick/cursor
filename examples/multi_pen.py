import cursor.path as path
import cursor.device as device
import cursor.export as export

if __name__ == "__main__":
    pc = collection.Collection()

    p1 = path.Path()
    p1.add(0, 0)
    p1.add(-1, 0)
    p1.pen_select = 1

    p2 = path.Path()
    p2.add(-1, 0)
    p2.add(1, 1)
    p2.pen_select = 2

    p3 = path.Path()
    p3.add(1, 1)
    p3.add(0, 1)
    p3.pen_select = 3

    p4 = path.Path()
    p4.add(0, 1)
    p4.add(0, 0)
    p4.pen_select = 4

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)

    export.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "multi_pen",
        "rect",
    )
