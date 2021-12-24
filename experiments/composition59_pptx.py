from cursor.path import Path, Spiral, PathCollection
from cursor import device

import random

if __name__ == "__main__":
    coll = PathCollection()

    for i in range(16):
        x = i % 4
        y = (i - x) / 4
        pp = Path(layer=f"{i:02d}")
       # pp = Path(layer="1")
        spiral = Spiral()
        spiral.max_theta = 255
        spiral.xoffset_incr = 0.1 + random.random() * 1.0  # random.random() * 1.0
        p = spiral.custom(pp)
        p.translate(x * 2250, y * 250)
        coll.add(p)

    name = "pptx"
    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "composition59_pptx_layer3",
        name,
    )
