from cursor import device
from cursor import path
from cursor import filter
from cursor import data
from cursor import loader

import sys
import math

if __name__ == "__main__":
    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=30)
    all_paths = _loader.all_paths()

    min_point_filter = filter.MinPointCountFilter(10)
    all_paths.filter(min_point_filter)

    max_point_filter = filter.MaxPointCountFilter(50)
    all_paths.filter(max_point_filter)

    for times in range(50):
        pc = path.PathCollection()

        r = all_paths.random()
        r.clean()
        pc.add(r)
        for i in range(10):
            pc.add(pc[0].offset(-0.0005 * i))
        for i in range(500):  # für a1 400
            pc.add(pc[0].offset(-0.001 * i))
        for i in range(10):
            pc.add(pc[0].offset(-0.0005 * (1000 - i)))

        device.SimpleExportWrapper().ex(
            pc,
            device.PlotterType.HP_7595A_A3,
            device.PaperSize.LANDSCAPE_A3,
            25,
            "composition73",
            f"200_tighter{times}",
        )
