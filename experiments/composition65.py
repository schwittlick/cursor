from cursor import loader
from cursor import data
from cursor import device
from cursor import filter


if __name__ == "__main__":
    recordings = data.DataDirHandler().recordings()
    l = loader.Loader(directory=recordings)
    all_paths = l.all_paths()

    distance_filter = filter.DistanceFilter(0.01)
    all_paths.filter(distance_filter)

    device.SimpleExportWrapper().ex(
        all_paths,
        device.PlotterType.ROLAND_DXY1200,
        device.PaperSize.LANDSCAPE_A3,
        15,
        "composition65",
        f"c65_{all_paths.hash()}",
    )
