from cursor import renderer
from cursor import path
from cursor import data
from cursor import device

import math


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0)
    jpeg_renderer.save(fname)


def two_split_spiral():
    pc = path.PathCollection()

    theta = 0
    yextra = 0
    r = 50
    perc = 0.35

    p1 = path.Path(layer="top")
    p2 = path.Path(layer="bottom")

    while theta < 801:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        theta += 0.02
        yextra += 0.01

        if theta < 800 * perc:
            p1.add(x, y)
        elif theta > 800 - 800 * 0.352:
            p2.add(x, y)

    pc.add(p1)
    pc.add(p2)

    return "two_split_spiral", pc


def middle_split_spiral():
    pc = path.PathCollection()

    theta = 0
    yextra = 0
    r = 50
    perc1 = 0.15
    perc2 = 0.4

    p1 = path.Path(layer="top")
    p2 = path.Path(layer="middle")
    p3 = path.Path(layer="bottom")

    while theta < 800:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        theta += 0.02
        yextra += 0.01

        if theta < 800 * perc1:
            p1.add(x, y)
        elif 800 * perc1 < theta < 800 * perc2:
            p2.add(x, y)
        else:
            p3.add(x, y)

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)

    return "middle_split_spiral", pc


def three_split_spiral():
    pc = path.PathCollection()

    theta = 0
    yextra = 0
    r = 50
    perc = 0.2

    p1 = path.Path(layer="top")
    p2 = path.Path(layer="middle")
    p3 = path.Path(layer="bottom")

    while theta < 800:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        theta += 0.02
        yextra += 0.015

        if theta < 800 * perc:
            p1.add(x, y)
        elif 800 / 2 - 800 * perc / 2 < theta < 800 / 2 + 800 * perc / 2:
            p2.add(x, y)
        elif theta > 800 - 800 * perc:
            p3.add(x, y)

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)

    return "three_split_spiral", pc


def dual_upward_spiral():
    pc = path.PathCollection()

    pp1 = path.Path(layer="top")
    pp2 = path.Path(layer="bottom")

    theta = 0
    yextra = 0
    r = 1
    while theta < 940:
        r += 0.03
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp1.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    theta = 0
    yextra = 0
    r = 1411
    while theta < 940:
        r -= 0.03
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp2.add(x, y, 0)
        theta += 0.02
        yextra += 0.15

    pc.add(pp1)
    pc.add(pp2)

    return "dual_upward_spiral", pc


def left_right_split_spiral():
    pc = path.PathCollection()

    pp1 = path.Path(layer="left")
    pp2 = path.Path(layer="right")

    theta = 0
    yextra = 0
    r = 50
    while theta < 801:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra
        pp1.add(x, y, 0)
        theta += 0.02
        yextra += 0.01

    theta = 0
    yextra = 0
    r = 50
    while theta < 801:
        y = (r * math.cos(theta) * 2) + 100
        x = r * math.sin(theta) + yextra
        pp2.add(x, y, 0)
        theta += 0.02
        yextra += 0.01

    pc.add(pp1)
    pc.add(pp2)

    return "left_right_split_spiral", pc


def many_split_left_right():
    pc = path.PathCollection()

    path_list1 = []
    path_list2 = []

    parts = 8
    for i in range(parts):
        p1 = path.Path(layer=f"left_{i}")
        p2 = path.Path(layer=f"right_{i}")

        path_list1.append(p1)
        path_list2.append(p2)

    c1 = get_random_chunksizes(parts, 801)
    c2 = get_random_chunksizes(parts, 801)

    theta = 0
    yextra = 0
    r = 50
    curr = 0
    while theta < 801:
        y = r * math.cos(theta) * 2
        x = r * math.sin(theta) + yextra

        if c1[curr] < theta < c1[curr + 1]:
            path_list1[curr].add(x, y)

        if theta > c1[curr + 1]:
            curr += 1

        theta += 0.02
        yextra += 0.01

    theta = 0
    yextra = 0
    r = 50
    curr = 0
    while theta < 801:
        y = (r * math.cos(theta) * 2) + 200
        x = r * math.sin(theta) + yextra

        if c2[curr] < theta < c2[curr + 1]:
            path_list2[curr].add(x, y)

        if theta > c2[curr + 1]:
            curr += 1

        theta += 0.02
        yextra += 0.01

    for p in path_list1:
        pc.add(p)

    for p in path_list2:
        pc.add(p)

    return "many_split_left_right", pc


def triple_fat_spiral():
    pc = path.PathCollection()

    p1 = path.Path(layer="left")
    p2 = path.Path(layer="middle")
    p3 = path.Path(layer="right")

    theta = 0
    yextra = 0
    r = 50
    while theta < 801:
        x = r * math.cos(theta) * 2
        y = r * math.sin(theta) + yextra
        p1.add(x, y, 0)
        theta += 0.02
        yextra += 0.01

    theta = 0
    yextra = 0
    r = 50
    while theta < 801:
        x = r * math.cos(theta) * 2 + 220
        y = r * math.sin(theta) + yextra
        p2.add(x, y, 0)
        theta += 0.02
        yextra += 0.01

    theta = 0
    yextra = 0
    r = 50
    while theta < 801:
        x = r * math.cos(theta) * 2 + 440
        y = r * math.sin(theta) + yextra
        p3.add(x, y, 0)
        theta += 0.02
        yextra += 0.01

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)

    return "triple_fat_spiral", pc


def get_random_chunksizes(chunknum, maxchunk):
    splits = chunknum
    import random

    randnumbers = []
    for _ in range(splits):
        newrand = random.randint(0, 1000)
        randnumbers.append(newrand)

    summe = sum(randnumbers)

    curr = 0.0

    chunks = [0]
    for i in range(splits):
        chunk = (randnumbers[i] / summe) * maxchunk
        chunks.append(chunk + curr)

        curr += chunk

    for c in chunks:
        print(c)

    return chunks


if __name__ == "__main__":
    coll = path.PathCollection()

    # num, pc = two_split_spiral()
    # num, pc = three_split_spiral()
    # num, pc = middle_split_spiral()
    # num, pc = dual_upward_spiral()
    # num, pc = left_right_split_spiral()
    # num, pc = many_split_left_right()
    num, pc = triple_fat_spiral()

    pc.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=90)
    save_wrapper(pc, "composition59_split", f"composition59_split_{num}_together")

    for p in pc:
        p_rev = p.reversed()
        p_rev.layer = p_rev.layer + "_rev"

        coll.add(p)
        coll.add(p_rev)

    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.DIY_PLOTTER,
        device.PaperSize.LANDSCAPE_A1,
        90,
        "composition59_split",
        num,
    )
    device.SimpleExportWrapper().ex(
        coll,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        90,
        "composition59_split",
        num,
    )
