import cursor.device as device
import cursor.export as export
import cursor.path as path


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
        device.PlotterType.HP_7470A,
        device.PaperSize.LANDSCAPE_A4,
        15,
        "simple_rect_example",
        "simple_rect",
    )
