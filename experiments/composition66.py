from cursor.path import Path, PathCollection
from cursor.renderer import RealtimeRenderer
from cursor import device

import math


def plain_spiral():
    pp = Path(layer="round1")
    length = 1500
    theta = 0
    ypos = 0
    r = 100
    x = 0
    while x < length:  # * 20:
        y = r * math.cos(theta)
        x = r * math.sin(theta) + ypos
        pp.add(x, y, 0)
        theta += 0.3
        ypos += 0.25

    return pp


if __name__ == "__main__":
    coll = PathCollection()

    p1 = plain_spiral()
    p2 = p1.copy().morph((0, 0), (1, 0))
    p3 = p1.copy().morph((0, 0.5), (1, 0.5))
    p4 = p1.copy().morph((0, 0), (0, 0.25))
    p5 = p1.copy()
    p5.rotate(2.0)

    num = "ad_strauss"

    # reversed_path = pp.reversed()
    # reversed_path.layer = "round2"

    # coll.add(p1)
    coll.add(p2)
    coll.add(p3)
    coll.add(p4)
    #coll.add(p5)
    # coll.add(reversed_path)

    # r = RealtimeRenderer()
    # r.render(coll)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        50,
        "composition66",
        num,
    )
