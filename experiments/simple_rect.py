from cursor import data
from cursor import device
from cursor import path
from cursor import renderer


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


def with_layers() -> "path.PathCollection":
    pc = path.PathCollection()

    p1 = path.Path(layer="1")
    p1.add(0, 0)
    p1.add(1, 0)

    p2 = path.Path(layer="2")
    p2.add(1, 0)
    p2.add(1, 1)

    p3 = path.Path(layer="3")
    p3.add(1, 1)
    p3.add(0, 1)

    p4 = path.Path(layer="4")
    p4.add(0, 1)
    p4.add(0, 0)

    # pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=10)
    # save_wrapper(pc, "millimeter", f"millimeter_papier")

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)

    return pc


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
    # pc = with_layers()

    layer_pen_mapping = {}
    layer_pen_mapping["1"] = 1
    layer_pen_mapping["2"] = 2
    layer_pen_mapping["3"] = 3
    layer_pen_mapping["4"] = 4

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        100,
        "simple_rect",
        "simple_rect",
        gcode_layer_pen_mapping=layer_pen_mapping,
    )
