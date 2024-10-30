import pathlib

import arcade.key
from pycocotools.coco import COCO

from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.position import Position
from cursor.collection import Collection
from cursor.bb import BoundingBox
from cursor.renderer.realtime import RealtimeRenderer


def output_cathegory(coco, cat, index):
    catIds = coco.getCatIds(catNms=cat)
    imgIds = coco.getImgIds(catIds=catIds)
    out = []
    assert index < len(imgIds), "Index out of range"
    img = coco.loadImgs(imgIds[index])[0]
    annIds = coco.getAnnIds(imgIds=img["id"], catIds=catIds, iscrowd=None)
    anns = coco.loadAnns(annIds)
    for outline in anns:
        if isinstance(outline["segmentation"], list):
            ol = outline["segmentation"]
            out.append(ol[0])

    return out


def to_coll(out):
    co = Collection()

    for d in out:
        c = 0
        p = Path()
        pos = Position()
        for current_pos in d:
            if c % 2 == 0:
                pos.x = current_pos
            else:
                pos.y = current_pos
                p.add(pos.x, pos.y, 0)
                pos = Position()
            c += 1

        p.add(d[0], d[1], 0)  # add first one to close shape
        co.add(p)

    return co


def next(rr: RealtimeRenderer):
    rr.clear()
    rr.clear_list()
    collections = []
    for cat in cats:
        if cat["name"] == "horse":
            out = output_cathegory(coco, cat, rr.global_index)
            c = to_coll(out)
            collections.append((cat, c))

    res = (2000, 1400)
    for co in collections:
        co[1].scale(1, -1)
        co[1].fit(BoundingBox(0, 0, res[0], res[1]), keep_aspect=True)
        co[1].simplify(0.01)
        rr.add_collection(co[1])

    rr.global_index += 1


if __name__ == "__main__":
    data_dir = DataDirHandler().data_dir
    data_type = "train2017"
    ann_file = data_dir / f"instances_{data_type}.json"

    p = pathlib.Path(ann_file)
    p.resolve()
    coco = COCO(p.absolute())

    cats = coco.loadCats(coco.getCatIds())
    collections = []

    for cat in cats:
        if cat["name"] == "horse":
            out = output_cathegory(coco, cat, 0)
            c = to_coll(out)
            collections.append((cat, c))

    res = (2000, 1400)
    for co in collections:
        co[1].scale(1, -1)
        co[1].fit(BoundingBox(0, 0, res[0], res[1]), keep_aspect=True)
        co[1].simplify(0.01)

    rr = RealtimeRenderer(res[0], res[1], "coco")
    rr.global_index = 1
    for co in collections:
        rr.add_collection(co[1], 1)
    rr.add_cb(arcade.key.N, next)
    rr.run()
