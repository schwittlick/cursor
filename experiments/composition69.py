from cursor import device
from cursor import path
from cursor import misc

def four_blocks():
    pc = path.PathCollection()

    for block in range(4):
        count = 390
        for v in range(count):
            pa = path.Path(pen_velocity=int(misc.map(v, 0, count, 45, 1, True)))
            v += block * count
            pa.add(v, 0)
            pa.add(v, 10)
            pa.pen_select = block + 1
            pc.add(pa)

    return pc


def alternating():
    pc = path.PathCollection()

    count = 390
    for v in range(count):
        if v % 2 == 0:
            velo = 1
        else:
            velo = 45
        pa = path.Path(pen_velocity=int(velo))
        pa.add(v, 0)
        pa.add(v, 10)
        #pa.pen_select = (count % 2) + 1
        pc.add(pa)

    return pc

if __name__ == "__main__":

    #pc = four_blocks()
    pc = alternating()

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        30,
        "composition69",
        f"c69_alternating_{pc.hash()}",
    )
