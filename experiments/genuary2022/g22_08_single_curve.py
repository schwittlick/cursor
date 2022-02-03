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
    loader = loader.Loader(directory=recordings, limit_files=1)
    pc = loader.all_paths()

    sorter = filter.Sorter(reverse=True, param=filter.Sorter.SHANNON_DIRECTION_CHANGES)
    pc.sort(sorter)

    pc_final = path.PathCollection()

    chosen = pc.random()

    bb = chosen.bb()

    pa = path.Path()
    pa.add(bb.x, bb.y)
    pa.add(bb.w, bb.h)

    times = 45
    for i in range(times):
        morphed = pa.interp(chosen, (1/times) * i)
        morphed.velocity = 80
        pc_final.add(morphed)

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_08_single_curve",
        f"random_{pc_final.hash()}",
    )
