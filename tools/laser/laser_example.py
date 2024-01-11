from cursor.collection import Collection
from cursor.device import PlotterType, PaperSize
from cursor.export import ExportWrapper
from cursor.path import Path

if __name__ == '__main__':
    c = Collection()
    for i in range(1, 21):
        p = Path()
        p.add(i, 0)
        p.add(i, 1)

        p.velocity = i * 5

        c.add(p)

    ExportWrapper().ex(
        c,
        PlotterType.ROLAND_DXY1200_A3,
        PaperSize.LANDSCAPE_A4,
        30,
        "laser_test",
        f"pwm_lines_{c.hash()}",
        keep_aspect_ratio=False,
    )
