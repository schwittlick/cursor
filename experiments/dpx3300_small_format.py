from cursor import device
from cursor import path


def regular() -> "path.PathCollection":
    pc = path.PathCollection()

    p = path.Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)
    pc.add(p)
    return pc


if __name__ == "__main__":
    pc = regular()

    layer_pen_mapping = {}
    layer_pen_mapping["1"] = 1
    layer_pen_mapping["2"] = 2
    layer_pen_mapping["3"] = 3
    layer_pen_mapping["4"] = 4

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A4,
        10,
        "simple_rect_10mm_margin",
        "simple_rect",
        # hpgl_pen_layer_mapping=layer_pen_mapping,
    )
