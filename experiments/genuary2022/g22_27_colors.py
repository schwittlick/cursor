import random

from cursor import device
from cursor import path
from cursor import data
from cursor import loader
from cursor import misc
from cursor import filter

import math
import numpy as np

if __name__ == "__main__":
    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=1)
    pc = _loader.all_paths()

    entropy_filter_min = filter.EntropyMinFilter(1.5, 1.5)
    pc.filter(entropy_filter_min)

    entropy_filter_max = filter.EntropyMaxFilter(2.5, 2.5)
    pc.filter(entropy_filter_max)

    point_filter = filter.MinPointCountFilter(30)
    pc.filter(point_filter)

    point_filter = filter.MaxPointCountFilter(100)
    pc.filter(point_filter)

    out = path.PathCollection()

    wid = 400

    for i in range(400):
        if random.uniform(0, 1) < 0.8:
            r1 = random.uniform(0, 0.9)
            r2 = random.uniform(0.05, 0.1)

            p1 = path.Path()
            p1.add(i, 0)
            p1.add(i, r1 * wid)
            p1.pen_select = 1
            out.add(p1)

            p2 = path.Path()
            p2.add(i, (r1 + r2)*wid)
            p2.add(i, 1* wid)
            p2.pen_select = 1
            out.add(p2)

            pr = pc.random()
            prm = pr.morph((i, r1 * wid),(i, (r1+r2)*wid))
            bb = prm.bb()
            bb2 = path.BoundingBox(-3, -3, 410, 410)
            while not bb2.inside(prm):
                print("try")
                pr = pc.random()
                prm = pr.morph((i, r1 * wid),(i, (r1+r2)*wid))
            #out.add(pr.morph((0, 0),(1, 1)))
            prm.pen_select = 2
            out.add(prm)
        else:
            p1 = path.Path()
            p1.add(i, 0)
            p1.add(i, wid)
            p1.pen_select = 1
            out.add(p1)

    sorter = filter.Sorter(param=filter.Sorter.PEN_SELECT, reverse=True)
    out.sort(sorter)

    device.SimpleExportWrapper().ex(
        out,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_27_colors",
        f"try1_{out.hash()}",
    )
