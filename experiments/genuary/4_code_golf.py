from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter


if __name__ == "__main__":
    recs = data.DataDirHandler().recordings()
    loader = loader.Loader(directory=recs, limit_files=None)
    all_paths = loader.all_paths()

    sorter = filter.Sorter(param=filter.Sorter.SHANNON_DIRECTION_CHANGES, reverse=True)
    all_paths.sort(sorter)

    pc = path.PathCollection()

    counter = 0
    for p in all_paths[:10]:
        p.layer = counter
        pc.add(p)

        counter += 1

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A1,
        90,
        "genuary",
        f"4_code_golf_ALL_{pc.hash()}",
    )
