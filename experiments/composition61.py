from cursor import loader
from cursor import data
from cursor import device
from cursor import filter

from cursor.filter import Sorter
from cursor.path import PathCollection

if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)
    pcol = ll.all_paths()
    # pcol.clean()

    entropy_filter = filter.EntropyMaxFilter(3.5, 3.5)
    # pcol.filter(entropy_filter)

    mincount_filter = filter.MinPointCountFilter(40)
    pcol.filter(mincount_filter)

    maxtraveldistance_filter = filter.DistanceFilter(0.06)
    pcol.filter(maxtraveldistance_filter)

    sorter = Sorter(param=Sorter.SHANNON_DIRECTION_CHANGES, reverse=False)
    pcol.sort(sorter)

    coll = PathCollection()

    for i in range(10):
        p = pcol[i]

        pnew = p.morph((i, 0), (i, 100))
        coll.add(pnew)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.HP_7475A,
        device.PaperSize.PORTRAIT_A4,
        20,
        "composition61",
        coll.hash(),
    )
