from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter

import random


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=6)
    jpeg_renderer.save(fname)


if __name__ == "__main__":
    random.seed(7)

    recs = data.DataDirHandler().recordings()
    loader = loader.Loader(directory=recs, limit_files=None)
    all_paths = loader.all_paths()
    all_paths.clean()

    pc = path.PathCollection()

    p1 = all_paths.random()
    #pc.add(p1)

    p2 = path.Path()
    p2.add(0, 0)
    p2.add(100, 100)
    p2.add(200, 100)
    p2.add(200, 200)
    p2.add(300, 200)
    p2.add(400, 200)
    p2.add(400, 100)

    pc.add(p2)
    #pc.add(p1)

    c = p2.direction_changes_pos_neg()
    c2 = p1.direction_changes_pos_neg()

    counterPos = 0
    counterNeg = 0
    for change in c:
        print(change)
        if change > 0:
            counterPos += change
        elif change < 0:
            counterNeg += change



    #ff = filter.Sorter(reverse=False, param=filter.Sorter.SHANNON_DIRECTION_CHANGES)
    #all_paths.sort(ff)

    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
    save_wrapper(pc, "genuary", f"16_circles_only_1")

    for pa in all_paths:
        direction_changes = pa.direction_changes_pos_neg()
        counterPos = 0
        counterNeg = 0
        for change in direction_changes:
            #print(change)
            if change > 0:
                counterPos += change
            elif change < 0:
                counterNeg += change

        relPos = counterPos / len(pa)
        relNeg = counterNeg / len(pa)

        #if abs(relNeg) > 90 or relPos > 90:
        #    print(pa.hash)
        #    print(f"neg: {relNeg}")
        #    print(f"pos: {relPos}")
        #    pc = path.PathCollection()
        #    pc.add(pa)
        #    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
        #    save_wrapper(pc, "genuary", f"16_circles_only_1{pa.hash}")

        if abs(counterNeg) > counterPos*10:
            print(pa.hash)
            print(f"neg: {counterNeg}")
            print(f"pos: {counterPos}")
            pc = path.PathCollection()
            pc.add(pa)
            pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
            save_wrapper(pc, "genuary", f"16_circles_only_1{pa.hash}")

        if counterPos > abs(counterNeg)*10:
            print(pa.hash)
            print(f"neg: {counterNeg}")
            print(f"pos: {counterPos}")
            pc = path.PathCollection()
            pc.add(pa)
            pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
            save_wrapper(pc, "genuary", f"16_circles_only_1{pa.hash}")