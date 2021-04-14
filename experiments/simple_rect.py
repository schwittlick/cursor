from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter

import random


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    pc = path.PathCollection()

    p = path.Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)

    # pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=10)
    # save_wrapper(pc, "millimeter", f"millimeter_papier")

    pc.add(p)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A,
        device.PaperSize.LANDSCAPE_80_50,
        50,
        "simple_rect",
        f"simple_rect",
    )
