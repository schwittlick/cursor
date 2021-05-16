from cursor.path import Path, PathCollection
from cursor.renderer import RealtimeRenderer
from cursor import device

import math


def plain_spiral(thetamax, yoffset, yadd, xextra):
    pp = Path(layer="round1")
    theta = 0
    ypos = 0
    xpos = 0
    r = 30
    while theta < thetamax: #* 20:
        y = r * math.cos(theta) + xpos
        x = r * math.sin(theta) + ypos
        pp.add(x, y + yoffset, 0)
        theta += 0.08
        ypos += yadd
        xpos += xextra

    return pp


if __name__ == "__main__":
    coll = PathCollection()

    xplus = 0.25
    yplus = 0.25

    p1 = plain_spiral(255, 0, xplus, 0)
    p2 = plain_spiral(255, 400, xplus, 0)
    p3 = plain_spiral(155, 0, 0, yplus)
    p4 = plain_spiral(155, 0, xplus, yplus)

    num = 'ad_strauss'

    # reversed_path = pp.reversed()
    # reversed_path.layer = "round2"

    coll.add(p1)
    coll.add(p2)
    coll.add(p3)
    coll.add(p4)
    # coll.add(reversed_path)

    #r = RealtimeRenderer()
    #r.render(coll)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        50,
        "composition66",
        num,
    )
