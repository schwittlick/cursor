from cursor import collection
from cursor import renderer
from cursor import data
from cursor import device
from cursor import filter
from cursor import loader

realtime_renderer = None


def save_callback(id: int, pc: collection.Collection):
    global realtime_renderer
    realtime_renderer.set([pc])


if __name__ == "__main__":
    res = device.Paper.sizes[device.PaperSize.LANDSCAPE_A1]
    p = data.DataDirHandler().recordings()
    files = ["1644923397.358839_compressed"]
    ll = loader.Loader(directory=p, limit_files=files)
    colls = ll.all_paths()

    min_filter = filter.MinPointCountFilter(250)
    colls.filter(min_filter)

    colls.limit()
    pcs = []

    ra = colls.random()
    num = 100
    for i in range(1, num):
        c = collection.Collection()
        _ra = ra.copy()
        _ra.downsample(i * 0.001)
        c.add(_ra)
        c.fit(res, padding_mm=10, keep_aspect=True)
        pcs.append(c)

    realtime_renderer = renderer.RealtimeRenderer(*res)
    realtime_renderer.set_cb(save_callback)
    realtime_renderer.set(pcs)
    realtime_renderer.render()
