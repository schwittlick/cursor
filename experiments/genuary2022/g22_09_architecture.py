from cursor import device
from cursor import path
from cursor import data
from cursor import loader
from cursor import misc


def get_two_with_intersect(pc):
    p1 = pc.random()
    p2 = pc.random()

    intersect, x, y = p1.intersect(p2)
    while not intersect:
        p1 = pc.random()
        p2 = pc.random()
        intersect, x, y = p1.intersect(p2)

    return p1, p2


def intersects(pc, p1, p2):
    for pa in pc:
        if pa.intersect(p1)[0]:
            return True
        if pa.intersect(p2)[0]:
            return True

    return False


if __name__ == "__main__":
    recordings = data.DataDirHandler().recordings()
    _loader = loader.Loader(directory=recordings, limit_files=15)
    pc = _loader.all_paths()

    amount = 16

    pc_final = path.PathCollection()
    timer = misc.Timer()
    timer.start()
    for i in range(amount):
        print(i)
        i11, i12 = get_two_with_intersect(pc)
        does_intersect = intersects(pc_final, i11, i12)
        c = 0

        while does_intersect:
            if c % 10 == 0:
                print(f"elapsed time {timer.elapsed()}")
            i11, i12 = get_two_with_intersect(pc)
            does_intersect = intersects(pc_final, i11, i12)
            c += 1

        i11.pen_select = i + 1
        i12.pen_select = i + 1
        i11.velocity = 10
        i12.velocity = 10
        pc_final.add(i11)
        pc_final.add(i12)

    for i in range(amount):
        pc_final[i].layer = "layer1"

    for i in range(amount):
        pc_final[i + amount].layer = "layer2"

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_09_architecture",
        f"controlled_overlap_{pc_final.hash()}",
    )
