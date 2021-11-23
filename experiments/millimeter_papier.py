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


if __name__ == "__main__":
    pc = path.PathCollection()

    for y in range(30):
        p = path.Path()
        for x in range(42):

            p.add(x, y)
            p.add(x + 1, y)
        pc.add(p)

    for x in range(42):
        p = path.Path()
        for y in range(30):
            p.add(x, y)
            p.add(x, y + 1)
        pc.add(p)

    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=10)
    svg_save_wrapper(pc, "millimeter", "millimeter_papier")

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A,
        device.PaperSize.LANDSCAPE_A0,
        10,
        "millimeter",
        f"millimeter_papier_spacing{10}",
    )
