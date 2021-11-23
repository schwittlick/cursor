from cursor import device
from cursor import path
from cursor import misc

if __name__ == "__main__":
    pc = path.PathCollection()

    count = 400
    max_phase = count
    mapping = {}
    for v in range(count):
        mapping[v] = f"2,{int(misc.map(v, 0, count, 1, max_phase, False))}"

        pa = path.Path(ptype=v)
        pa.add(0, count * 10 - (v * 10))
        pa.add(100, count*10 - (v * 10))
        pc.add(pa)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_PNC1000,
        device.PaperSize.PORTRAIT_50_80,
        50,
        "composition68",
        f"c68_{pc.hash()}",
        #hpgl_linetype_mapping=mapping
    )
