from cursor.path import Path, PathCollection
from cursor import device

import math


def plain_spiral(pp):
    theta = 0
    yextra = 0
    r = 50
    while theta < 255:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    return "spiral_plain"


def full_spiral(pp, rounds=800, _yextra=0.01, _theta=0.02):
    theta = 0
    yextra = 0
    r = 50
    while theta < rounds:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += _theta
        yextra += _yextra

    return "full_plain"


def double_full_spiral1(pp, rounds=800, _yextra=0.01, _theta=0.02):
    theta = 0
    yextra = 0
    r = 50
    while theta < rounds:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += _theta
        yextra += _yextra


    return "double_full_spiral1"


def double_full_spiral2(pp, rounds=800, _yextra=0.01, _theta=0.02):
    theta = 0
    yextra = 0
    r = 50

    while theta < rounds:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x + 100, y, 0)
        theta += _theta
        yextra += _yextra

    return "double_full_spiral2"


def circleball_spiral(pp):
    theta = 0
    yextra = 0
    r = 1
    while theta < 255:
        r += 0.4
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    return "circleball_spiral"


def upward_spiral(pp):
    theta = 0
    yextra = 0
    r = 1
    while theta < 940:
        r += 0.03
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    return "upward_spiral"


def heart_spiral(pp):
    theta = 0
    yextra = 0
    while theta < 800:
        r = (math.sin(theta) * 500) + 500
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.02
        yextra += 0.06

    return "heart_spiral"


def fat_spiral(pp):
    theta = 0
    yextra = 0
    r = 50
    while theta < 6000:
        x = r * math.cos(theta) * 2
        y = r * math.sin(theta) + yextra
        pp.add(x, y, 0)
        theta += 0.005
        yextra += 0.01

    return "fat_spiral"


if __name__ == "__main__":
    coll = PathCollection()

    pp = Path(layer="top")
    pp2 = Path(layer="bottom")

    # num = plain_spiral(pp)
    # num = circleball_spiral(pp)
    # num = upward_spiral(pp)
    # num = full_spiral(pp, 20000, 0.0005, 0.1)
    # num = heart_spiral(pp)
    # num = fat_spiral(pp)
    name = double_full_spiral1(pp, 20000, 0.0005, 0.1)
    name2 = double_full_spiral2(pp2, 20000, 0.0005, 0.1)

    #reversed_path = pp.reversed()
    #reversed_path.layer = "round2"

    coll.add(pp)
    coll.add(pp2)

    # device.SimpleExportWrapper().ex(
    #    coll,
    #    device.PlotterType.DIY_PLOTTER,
    #    device.PaperSize.LANDSCAPE_A3,
    #    40,
    #    "composition59",
    #    num,
    # )

    # device.SimpleExportWrapper().ex(
    #    coll,
    #    device.PlotterType.DIY_PLOTTER,
    #    device.PaperSize.LANDSCAPE_A1,
    #    90,
    #    "composition59",
    #    num,
    # )

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        35,
        "composition59",
        name,
    )
    # device.SimpleExportWrapper().ex(
    #    coll,
    #    device.PlotterType.AXIDRAW,
    #    device.PaperSize.LANDSCAPE_48_36,
    #    64,
    #    "composition59",
    #    num,
    # )
