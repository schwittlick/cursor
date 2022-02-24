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
    _loader = loader.Loader(directory=recordings, limit_files=1)
    all_paths = _loader.all_paths()

    r = all_paths.random()
    r.clean()
    pc.add(r)
    for i in range(100):
        pc.add(pc[0].offset(-0.002 * i))

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        30,
        "composition73",
        f"offset",
    )