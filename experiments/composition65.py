from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter


if __name__ == "__main__":
    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=None)
    all_paths = _loader.all_paths()

    distance_filter = filter.DistanceFilter(0.01)
    all_paths.filter(distance_filter)

    all_paths.limit()

    pc = path.PathCollection()

    counter = 0
    for p in all_paths:
        # p.layer = counter
        pc.add(p)

        counter += 1
        counter = counter % 6

    #pc.reorder_quadrants(10, 10)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DXY1200,
        device.PaperSize.LANDSCAPE_A3,
        15,
        "composition65",
        # f"c65_{pc.hash()}",
        "c65_001distance_unordered",
    )
