from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import filter


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    files = ["1630239844.869984_compressed"]
    files = ["1614949295.06338_compressed"]
    files = ["1618566653.673052_compressed"]
    files = ["1585761724.491215_compressed"]
    files = ["1587633175.47697_compressed"]
    _loader = loader.Loader(directory=p, limit_files=3)
    all_paths = _loader.all_paths()

    min_distance_filter = filter.MinDistanceFilter(1.5)
    max_distance_filter = filter.DistanceFilter(2)
    all_paths.filter(min_distance_filter)
    # all_paths.filter(max_distance_filter)

    all_paths.limit()

    pc = path.PathCollection()

    print(len(all_paths))

    counter = 0
    for p in all_paths:
        for _pa in p:
            _pa.translate(0, counter * 1)
        pc.add(p)

        counter += 1

    # pc.reorder_quadrants(10, 10)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_PNC1000,
        device.PaperSize.PORTRAIT_50_80,
        20,
        "composition67",
        f"c65_{pc.hash()}",
    )
