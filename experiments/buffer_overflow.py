from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter

import random
import math

def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


def circles():
    pc = path.PathCollection()

    r = 50

    for i in range(10):
        theta = 0
        yextra = 0
        r += 20
        pp = path.Path()
        while theta < 255:
            y = r * math.cos(theta)
            x = r * math.sin(theta)
            pp.add(x, y, 0)
            theta += 0.1

        pc.add(pp)
    # pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=10)
    # save_wrapper(pc, "circles", f"circles1")

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7475A_A3,
        device.PaperSize.LANDSCAPE_A3,
        60,
        "buffer_overflow",
        f"circles{10}",
    )

def patches():
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)

    all_paths = ll.all_paths()

    point_filter = filter.MaxPointCountFilter(100)
    all_paths.filter(point_filter)

    point_filter2 = filter.MinPointCountFilter(6)
    all_paths.filter(point_filter2)

    entropy_filter_min = filter.EntropyMinFilter(0.1, 0.1)
    all_paths.filter(entropy_filter_min)

    entropy_filter_max = filter.EntropyMaxFilter(2.0, 2.0)
    all_paths.filter(entropy_filter_max)

    pa = all_paths.random()
    pc = path.PathCollection()
    for i in range(200):
        mapped = pa.morph((i, 0), (i, 100))
        pc.add(mapped)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7475A_A3,
        device.PaperSize.LANDSCAPE_A3,
        40,
        "buffer_overflow",
        "patches1",
    )


if __name__ == "__main__":
    patches()
