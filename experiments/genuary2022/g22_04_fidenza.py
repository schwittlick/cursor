from cursor import device
from cursor import path
from cursor import data
from cursor import loader
from cursor import misc
from cursor import filter

import math


def get_ratio(dir_changes):
    count_neg = 0
    count_pos = 0
    zero = 0
    for change in dir_changes:
        if change < 0:
            count_neg += 1
        elif change == 0:
            zero += 1
        else:
            count_pos += 1
    return count_pos, count_neg, zero


def trying(vertices):
    return_vertices = []
    idx = 0
    prev = 0
    for _ in vertices:
        if idx > 0:
            f = vertices[idx - 1]
            s = vertices[idx]

            ang = math.atan2(s.y - f.y, s.x - f.x)
            ang = math.degrees(ang)

            fin = ang - prev
            if fin <= 0:
                return_vertices.append(_)
            prev = ang
        idx += 1

    return return_vertices


def stash():
    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=1)
    pc = _loader.all_paths()

    pc_final = path.PathCollection()

    for p in pc:
        p.vertices = trying(p.vertices)

        # changes_posneg = p.direction_changes_pos_neg()
        # changes = p.direction_changes()
        # ratio = get_ratio(changes_posneg)
        pc_final.add(p)

    print(len(pc_final))

    # sorter = filter.Sorter(param=filter.Sorter.PEN_SELECT, reverse=True)
    # pc.sort(sorter)

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_04_fidenza",
        "fff",
    )


def damn():
    import numpy as np
    import matplotlib.pyplot as plt

    r = 16 * 8
    n_priods = 8

    x, y = np.meshgrid(np.linspace(-(r / 2), r / 2, r), np.linspace(-(r / 2), r / 2, r))

    u = -y / np.sqrt(x ** 2 + y ** 2)
    v = x / np.sqrt(x ** 2 + y ** 2)

    noise = misc.generate_perlin_noise_2d((r, r), (n_priods, n_priods))

    pc_final = path.PathCollection()

    for __x in range(r):
        for __y in range(r):
            _nx = noise[__x][__y]
            _ny = noise[__x][__y]
            _x = x[__x][__y]
            _y = y[__x][__y]
            _u = u[__x][__y] + _nx
            _v = v[__x][__y] + _ny
            if math.isnan(_u) or math.isnan(_v):
                continue
            # print("lol")
            p = path.Path()
            p.add(_x, _y, 0)
            p.add(_x + _u, _y + _v, 0)
            pc_final.add(p)

    for p in pc_final:
        v = p.direction_changes()
        degrees = math.degrees(v[0])
        if degrees < 90:
            p.pen_select = 1
        if degrees >= 90 and degrees < 180:
            p.pen_select = 2
        if degrees >= 180 and degrees < 270:
            p.pen_select = 3
        if degrees >= 270:
            p.pen_select = 4
        print(v)

    sorter = filter.Sorter(param=filter.Sorter.PEN_SELECT, reverse=True)
    pc_final.sort(sorter)

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_04_fidenza",
        "fff_TEST_noise_pens",
    )
    plt.quiver(x, y, u, v)
    plt.show()


if __name__ == "__main__":
    # recordings = data.DataDirHandler().recordings()
    # _loader = loader.Loader(directory=recordings, limit_files=1)
    # pc = _loader.all_paths()

    pc_final = path.PathCollection()

    damn()

    # device.SimpleExportWrapper().ex(
    #    pc_final,
    #    device.PlotterType.HP_7595A_A3,
    #    device.PaperSize.LANDSCAPE_A3,
    #    25,
    #    "genuary22_04_fidenza",
    #    f"fff",
    # )
