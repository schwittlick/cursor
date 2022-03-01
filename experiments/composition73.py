from cursor import device
from cursor import path
from cursor import data
from cursor import loader


if __name__ == "__main__":
    pc = path.PathCollection()

    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=1)
    all_paths = _loader.all_paths()

    r1 = all_paths[1]
    r2 = r1.copy()

    r1.smooth(5, 1)

    pc.add(r1)
    # pc.add(r2)

    v = 0.05

    pc.add(pc[0].offset(v))
    pc.add(pc[0].offset(-v))
    # pc.add(pc[1].offset(v))
    # pc.add(pc[1].offset(-v))

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        30,
        "composition73",
        "offset",
    )
