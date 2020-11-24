from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data
from cursor import device


def composition56(nr, pathlist):
    xoffset = 0

    xspacing = 1
    coll = path.PathCollection()

    for p in pathlist:
        for i in range(250):
            xfrom = xspacing * i + xoffset
            yfrom = 0
            xto = xspacing * i + xoffset
            yto = 1000
            morphed = p.morph((xfrom, yfrom), (xto, yto))
            coll.add(morphed)

        xoffset += 400

    hash = pathlist[0].hash

    print(f"rendering {nr}, {coll.bb()}")

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A1,
        90,
        "composition56",
        hash,
    )


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=2)
    rec = ll.single(0)
    all_paths = ll.all_paths()

    entropy_filter = filter.EntropyMinFilter(1.2, 1.2)
    all_paths.filter(entropy_filter)

    distance_filter = filter.DistanceFilter(100)
    all_paths.filter(distance_filter)

    for i in range(1):
        r1 = all_paths.random()
        r2 = all_paths.random()
        r3 = all_paths.random()
        r4 = all_paths.random()
        r5 = all_paths.random()

        print(r1.hash)

        composition56(i, [r1, r2, r3, r4, r5])
