from cursor import path
from cursor import renderer
from cursor import device
from cursor import export


def save_callback(id: int, pc: "collection.Collection"):
    print(f"saving {id}")
    export.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        20,
        "realtime_example",
        f"switch_pathcollections_{id}",
    )


if __name__ == "__main__":
    pc1 = collection.Collection()
    pc2 = collection.Collection()

    p = path.Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)
    p.scale(600, 600)
    pc1.add(p)

    p2 = path.Path()
    p2.add(0, 0)
    p2.add(1, 0)
    p2.add(1, 1)
    p2.add(0, 1)
    p2.add(0, 0)
    p2.scale(40, 40)
    p2.translate(200, 200)
    pc2.add(p2)

    res = device.Paper.sizes[device.PaperSize.LANDSCAPE_A1]

    pc1.fit(res, padding_mm=10)
    pc2.fit(res, padding_mm=20, keep_aspect=True)

    pcs = []
    pcs.append(pc1)
    pcs.append(pc2)

    rr = renderer.RealtimeRenderer(*res)
    rr.set_cb(save_callback)
    rr.set(pcs)

    rr.render()
