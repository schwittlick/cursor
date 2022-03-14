from cursor import device
from cursor import path
from cursor import filter

import json
import time
import random
from alive_progress import alive_bar


def overlaps(pc, p):
    for line in pc:
        if line.intersect(p)[0]:
            return True

    return False


def file_to_paths(pc, file, pen):
    # pc = path.PathCollection()
    counter = 0
    contours = len(file)
    with alive_bar(contours) as bar:
        for d in file:
            c = 0
            p = path.Path()
            pos = path.Position()

            for current_pos in d:
                if c % 2 == 0:
                    pos.x = current_pos
                else:
                    pos.y = current_pos
                    p.add(pos.x, pos.y, 0)
                    pos = path.Position()
                c += 1

            p.add(d[0], d[1], 0)  # add first one to close shape
            # print(p.shannon_direction_changes)
            # p.pen_select = pen
            p.pen_select = random.randint(1, 4)
            # print(p.pen_select)

            p.translate(random.randint(0, 400), random.randint(0, 400))
            p.scale(0.1, 0.1)
            if not overlaps(pc, p):
                pc.add(p)
            time.sleep(0.00005)
            bar()
            counter += 1

    print(len(pc))
    return pc


if __name__ == "__main__":
    # categories = ['broccoli', 'bus', 'traffic_light', 'airplane', 'cat', 'boat', 'bicycle']
    categories = ["person"]
    pc_all = path.PathCollection()
    for cat in categories:
        # cat = "all"
        fname = f"{cat}.json"
        data = json.load(open(fname))
        print(f"done loading {fname}")
        file_to_paths(pc_all, data, categories.index(cat) + 1)

        # pc_all = pc_all + pc

    sorter = filter.Sorter(param=filter.Sorter.PEN_SELECT, reverse=True)
    pc_all.sort(sorter)

    device.SimpleExportWrapper().ex(
        pc_all,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_03_space",
        f"{'_'.join(categories)}_nooverlap_scaled_translated",
    )
