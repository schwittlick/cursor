import pathlib
from pycocotools.coco import COCO

from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.position import Position
from cursor.collection import Collection
from cursor.bb import BoundingBox
from cursor.renderer import RealtimeRenderer


def output_cathegory(coco, cat):
    catIds = coco.getCatIds(catNms=cat)
    imgIds = coco.getImgIds(catIds=catIds)
    out = []
    for i in range(len(imgIds)):
        selected = i
        img = coco.loadImgs(imgIds[selected])[0]
        annIds = coco.getAnnIds(imgIds=img["id"], catIds=catIds, iscrowd=None)
        anns = coco.loadAnns(annIds)
        for outline in anns:
            if type(outline["segmentation"]) == list:
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


if __name__ == "__main__":
    dataDir = ".."
    dataType = "train2017"
    annFile = "../data/annotations/instances_{}.json".format(dataType)

    p = pathlib.Path(annFile)
    p.resolve()
    coco = COCO(p.absolute())

    cats = coco.loadCats(coco.getCatIds())
    nms = [cat["name"] for cat in cats]
    print("COCO categories: \n{}\n".format(" ".join(nms)))

    # nms = set([cat["supercategory"] for cat in cats])
    # print("COCO supercategories: \n{}".format(" ".join(nms)))

    collections = []

    for cat in nms:
        out = output_cathegory(coco, cat)
        c = to_coll(out)
        collections.append((cat, c))

    res = (1920 - 200, 1080 - 200)
    for co in collections:
        for pa in co[1]:
            pa.fit(BoundingBox(0, 0, 1, 1), 0.8)

        co[1].simplify(0.01)

    su = Collection()
    for co in collections:
        su = su + co[1]

        # sorter = Sorter(param=SortParameter.ENTROPY_X, reverse=True)
        # co[1].sort(sorter)

        # fn = DataDirHandler().pickles() / "mscoco2017" / "train_each_cat" / f"{co[0]}_sorted_entropy_x.pickle"
        # co[1].save_pickle(fn.as_posix())

    # import sys
    # sys.exit()

    fn = DataDirHandler().pickles() / "mscoco2017" / "train_all_sorted_entropy_x.pickle"
    su.save_pickle(fn.as_posix())

    import sys

    sys.exit()

    rr = RealtimeRenderer(res[0], res[1], "coco")
    c = 0
    for co in collections:
        # fn = DataDirHandler().pickles() / "mscoco2017" / f"{co[0]}.pickle"
        # co[1].save_pickle(fn)
        co[1].translate(c * 10, 0)
        rr.add_collection(co[1], 1)
        c += 1
    rr.run()
