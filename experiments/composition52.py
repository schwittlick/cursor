from cursor import loader
from cursor import renderer
from cursor import path
from cursor import data
from cursor import filter
from cursor import device


def composition52(idx, pa):
    print(f"Creating Composition #52.{idx}")
    coll = path.PathCollection()

    xoffset = 135.38
    yoffset = 132.3

    xspacing = 2.5
    manual_less_x = 20

    for i in range(int(2138 / xspacing) - manual_less_x):  # 1042
        xfrom = xspacing * i + xoffset
        yfrom = yoffset
        xto = xspacing * i + xoffset
        yto = 1470 + yoffset
        morphed = pa.morph((xfrom, yfrom), (xto, yto))
        coll.add(morphed)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A1,
        90,
        "composition52",
        str(idx),
    )


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)

    all_paths = ll.all_paths()

    point_filter = filter.MaxPointCountFilter(100)
    all_paths.filter(point_filter)

    point_filter2 = filter.MinPointCountFilter(6)
    all_paths.filter(point_filter2)

    entropy_filter_min = filter.EntropyMinFilter(0.1, 0.1)
    all_paths.filter(entropy_filter_min)

    entropy_filter_max = filter.EntropyMaxFilter(2.0, 2.0)
    all_paths.filter(entropy_filter_max)

    for i in range(20):
        p = all_paths[i]
        composition52(i, p)
