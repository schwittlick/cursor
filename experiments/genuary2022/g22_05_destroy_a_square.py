from cursor import device
from cursor import path
from cursor import data
from cursor import loader
from cursor import misc
from cursor import filter

import numpy as np


def create_square(pieces: int = 100):
    pc_temp = path.PathCollection()

    for i in range(pieces):
        x1 = i
        y1 = 0

        x2 = i + 1
        y2 = 0

        pa = path.Path()
        pa.add(x1, y1)
        pa.add(x2, y2)

        pc_temp.add(pa)

    for i in range(pieces):
        x1 = pieces
        y1 = i

        x2 = pieces
        y2 = i + 1

        pa = path.Path()
        pa.add(x1, y1)
        pa.add(x2, y2)

        pc_temp.add(pa)

    for i in range(pieces):
        x1 = pieces - i
        y1 = pieces

        x2 = pieces + 1 - i
        y2 = pieces

        pa = path.Path()
        pa.add(x1, y1)
        pa.add(x2, y2)

        pc_temp.add(pa)

    for i in range(pieces):
        x1 = 0
        y1 = i

        x2 = 0
        y2 = i + 1

        pa = path.Path()
        pa.add(x1, y1)
        pa.add(x2, y2)

        pc_temp.add(pa)

    return pc_temp


def new_constellation():
    pc_temp = create_square(pieces)
    pc = path.PathCollection()

    indices = np.arange(pieces * 4)
    np.random.shuffle(indices)

    idx = 0
    for pa in pc_temp:
        pa_copy = pa.copy()
        pa_copy.vertices[1] = pc_temp[indices[idx]].vertices[1]
        pc.add(pa_copy)

        idx += 1
    return pc


def make_pen(pc):
    p = path.Path()
    index = 0
    for pa in pc:
        pa.pen_select = (i % 2) + 1
        index += 1


if __name__ == "__main__":
    # recordings = data.DataDirHandler().recordings()
    # _loader = loader.Loader(directory=recordings, limit_files=1)
    # pc = _loader.all_paths()

    pieces = 10

    pc_final = path.PathCollection()

    for i in range(20):
        pc2 = new_constellation()
        pc2.translate(i * 1, i * 2)
        make_pen(pc2)
        pc_final.extend(pc2)

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_05_destroy_square",
        f"shuffled_target_20_{pc_final.hash()}",
    )
