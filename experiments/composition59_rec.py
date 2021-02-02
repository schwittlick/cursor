from cursor.path import Path, PathCollection
from cursor import device

import math


def full_spiral(pp, rounds=200, _yextra=0.01, _theta=0.003):
    theta = 0
    yextra = 0
    xextra = 0
    r = 50
    r2 = 10
    # wenn mehr oder weniger spacing, r2 does the job
    theta2 = 0
    while theta < rounds:
        x2 = r2 * math.sin(theta2)
        y2 = r2 * math.cos(theta2) * 0.5

        x = r * math.sin(theta) + x2 + yextra
        y = r * math.cos(theta) + y2

        pp.add(x, y, 0)

        theta += _theta
        theta2 += 1.3
        yextra += _yextra

    return "full_plain"


if __name__ == "__main__":
    coll = PathCollection()

    pp = Path(layer="round1")

    num = full_spiral(pp)

    reversed_path = pp.reversed()
    reversed_path.layer = "round2"

    coll.add(pp)
    coll.add(reversed_path)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        70,
        "composition59_rec",
        num,
    )