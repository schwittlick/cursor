import random

from cursor import device
from cursor import path
from cursor import data
from cursor import loader
from cursor import filter

import time
from alive_progress import alive_bar


def intersects_any(pc, pa):

    for p in pc:
        if p.intersect(pa)[0]:
            return True
    return False


if __name__ == "__main__":
    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=2)
    pc = _loader.all_paths()

    pc_final = path.PathCollection()
    first = pc.random()

    pc_final.add(first)

    size = len(pc)
    c = 0
    with alive_bar(size) as bar:
        for pa in pc:
            bar()
            time.sleep(0.0001)
            print(f"{c}/{size} - {len(pc_final)}")
            # bar()
            pa.translate(random.random(), random.random())
            if not intersects_any(pc_final, pa):
                pa.pen_select = 1
                pa.velocity = 10
                pc_final.add(pa)
            c += 1

    sorter = filter.Sorter(reverse=True, param=filter.Sorter.DISTANCE)
    pc_final.sort(sorter)

    for pa in pc_final[:10]:
        pa.pen_select = 2

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_12_packing",
        f"one_file_{pc_final.hash()}",
    )
