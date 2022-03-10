from cursor import device
from cursor import path
from cursor import filter
from cursor import data
from cursor import loader

import sys
import math

if __name__ == "__main__":
    pc = path.PathCollection()

    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=None)
    all_paths = _loader.all_paths()

    w = 2
    h = 70 * 5

    fitting = []

    as_filter1 = filter.AspectRatioFilter(8, 100)
    all_paths.filter(as_filter1)

    # all_paths.clean()

    sorter = filter.Sorter(param=filter.Sorter.SHANNON_DIRECTION_CHANGES, reverse=True)
    all_paths.sort(sorter)

    print(len(all_paths))

    if len(all_paths) < w * h:
        print("exit")
        sys.exit(1)

    for x in range(w):
        for y in range(h):
            index = x + w * y
            p = all_paths[index]
            p.clean()
            p.velocity = 15
            p.move_to_origin()
            c = p.centeroid()
            bb = p.bb()
            _w = p.bb().w
            if _w == 0.0:
                _w = 0.001
            _h = p.bb().h
            if _h == 0.0:
                _h = 0.001
            xscale = (1 / _w) * 1.0
            yscale = (1 / _h) * 1.0
            p.scale(xscale, yscale)
            p.translate(x * 1, y * 1)
            pc.add(p)

    # remove lots of unnecessary close-by points from a path
    simplify_filter = filter.DistanceBetweenPointsFilter(0.008, 1.0)
    pc.filter(simplify_filter)

    pc.clean()
    pc.rot(-math.pi / 2)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "composition77",
        "top_bottom",
    )
