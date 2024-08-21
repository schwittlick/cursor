from cursor.renderer.realtime import RealtimeRenderer
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import PaperSize, Paper
from cursor.filter import MinPointCountFilter
from cursor.load.loader import Loader

if __name__ == "__main__":
    res = Paper.sizes[PaperSize.LANDSCAPE_A1]
    p = DataDirHandler().recordings()
    files = ["1644923397.358839_compressed"]
    ll = Loader(directory=p, limit_files=files)
    colls = ll.all_paths()

    min_filter = MinPointCountFilter(250)
    colls.filter(min_filter)

    colls.limit()
    pcs = []

    ra = colls.random()
    num = 100
    for i in range(1, num):
        c = Collection()
        _ra = ra.copy()
        _ra.downsample(i * 0.001)
        c.add(_ra)
        c.fit(res, padding_mm=10, keep_aspect=True)
        pcs.append(c)

    realtime_renderer = RealtimeRenderer(*res)
    for collection in pcs:
        realtime_renderer.add_collection(collection)
    realtime_renderer.render()
