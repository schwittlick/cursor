from cursor import device
from cursor import path
from cursor import filter

import json
import random
from alive_progress import alive_bar


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

            # p.translate(random.randint(0, 400), random.randint(0, 400))
            # p.scale(0.1, 0.1)
            pc.add(p)
            bar()
            counter += 1

    print(len(pc))
    return pc


def split_path_and_three_colors(pc, p):
    pass


def make_filled_polygon(pc):
    file = open("g22_18_three_colors.hpgl", "w")
    file.write("IN;\n")

    for pa in pc:
        file.write(f"SP{pa.pen_select};\n")
        file.write("PM0;\n")  # maybe not close it? 😈
        file.write(f"PA{int(pa[0].x)},{int(pa[0].y)};\n")
        for point in pa:
            file.write(f"PD{int(point.x)},{int(point.y)};\n")

        file.write("PM2;\n")  # maybe not close it? 😈
        file.write("FP;\n")  # maybe not close it? 😈

    file.close()


if __name__ == "__main__":
    # recordings = data.DataDirHandler().recordings()
    # _loader = loader.Loader(directory=recordings, limit_files=1)
    # pc = _loader.all_paths()

    categories = ["broccoli"]
    pc_all = path.PathCollection()
    for cat in categories:
        # cat = "all"
        fname = f"{cat}.json"
        data = json.load(open(fname))
        print(f"done loading {fname}")

        file_to_paths(pc_all, data, categories.index(cat) + 1)

    # sorter = filter.Sorter(param=filter.Sorter.POINT_COUNT, reverse=True)
    # pc_all.sort(sorter)
    # rs = pc_all[0]
    entropy_filter = filter.EntropyMinFilter(1.5, 1.5)
    point_filter1 = filter.MinPointCountFilter(100)
    point_filter2 = filter.MaxPointCountFilter(30)
    # pc_all.filter(point_filter1)
    # pc_all.filter(point_filter2)
    pc_all.clean()
    # pc_all.filter(entropy_filter)

    pc = path.PathCollection()

    rows = 3
    for i in range(rows * rows):
        # p = pc_all.random().copy()
        p = pc_all.random()
        split1 = random.uniform(0, 0.5)
        split2 = random.uniform(0.5, 1.0)

        end1 = int(len(p) * split1)
        end2 = int(len(p) * split2)

        p1 = path.Path(p.vertices[:end1])
        p2 = path.Path(p.vertices[end1:end2])
        p3 = path.Path(p.vertices[end2:])

        p1.pen_select = (((i % 3) + 1) % 3) + 1
        p2.pen_select = (((i % 3) + 2) % 3) + 1
        p3.pen_select = (((i % 3) + 3) % 3) + 1
        p1.is_polygon = True
        p2.is_polygon = True
        p3.is_polygon = True

        x = (i % rows) + 1
        y = (int(i / rows)) + 1

        center = p1.centeroid()
        p1.translate(-center[0], -center[1])
        pc1 = path.PathCollection()
        pc1.add(p1)
        pc1.fit((280, 280))
        p1 = pc1[0]
        p1.translate(300 * x, 300 * y)

        center = p2.centeroid()
        p2.translate(-center[0], -center[1])
        pc2 = path.PathCollection()
        pc2.add(p2)
        pc2.fit((280, 280))
        p2 = pc2[0]
        p2.translate(300 * x, 300 * y)

        center = p3.centeroid()
        p3.translate(-center[0], -center[1])
        pc3 = path.PathCollection()
        pc3.add(p3)
        pc3.fit((280, 280))
        p3 = pc3[0]
        p3.translate(300 * x, 300 * y)

        pc.add(p1)
        pc.add(p2)
        pc.add(p3)

        # rs2.translate(i * 1, i * 1)
        # pc.add(rs2)

    # pc.scale(10, 10)
    # make_filled_polygon(pc)

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        25,
        "genuary22_18_three_colors",
        f"split_path_{pc.hash()}",
    )
