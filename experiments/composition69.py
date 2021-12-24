from cursor import device
from cursor import path
from cursor import misc

if __name__ == "__main__":
    pc = path.PathCollection()
    count = 390
    for v in range(count):
        pa = path.Path(pen_velocity=int(misc.map(v, 0, count, 45, 1, True)))
        pa.add(v, 0)
        pa.add(v, 10)
        pc.add(pa)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        30,
        "composition69",
        f"c69_{pc.hash()}",
    )
