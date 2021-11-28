from cursor import device
from cursor import path
from cursor import loader
from cursor import data
from cursor import misc

if __name__ == "__main__":
    #p = data.DataDirHandler().recordings()
    #_loader = loader.Loader(directory=p, limit_files=3)
    #all_paths = _loader.all_paths()

    pc = path.PathCollection()
    count = 360
    for v in range(count):
        pa = path.Path(velocity=int(misc.map(v, 0, count, 45, 1, True)))
        pa.add(v, 0)
        pa.add(v, 10)
        pc.add(pa)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        60,
        "composition69",
        f"c69_{pc.hash()}",
    )
