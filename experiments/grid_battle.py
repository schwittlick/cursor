from cursor import data
from cursor import device
from cursor import path
from cursor import renderer


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


def svg_save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().svg(projname)
    svg_renderer = renderer.SvgRenderer(folder)

    svg_renderer.render(pc)
    svg_renderer.save(fname)


def rect(x, y):
    p = path.Path()
    p.add(0.2, 0.2)
    p.add(0.2, 0.8)
    p.add(0.8, 0.8)
    p.add(0.8, 0.2)
    p.add(0.2, 0.2)
    p.translate(x, y)
    return p


if __name__ == "__main__":
    pc = path.PathCollection()

    for y in range(30):
        p = path.Path()
        for x in range(41):

            p.add(x, y)
            p.add(x + 1, y)
            if x != 41:
                pc.add(rect(x, y))
        pc.add(p)

    for x in range(42):
        p = path.Path()
        for y in range(30):
            p.add(x, y)
            p.add(x, y + 1)
        pc.add(p)

    # pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A3], padding_mm=10)
    # svg_save_wrapper(pc, "grid_battle", "millimeter_papier")

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DXY1200,
        device.PaperSize.LANDSCAPE_A3,
        10,
        "grid_battle",
        "1_insides",
    )
