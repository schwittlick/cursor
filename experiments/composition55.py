from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data


def composition55(p0, p1, offset):
    gd = data.DataDirHandler().gcode("composition55")
    gcode_renderer = renderer.GCodeRenderer(gd, z_down=3.0)

    jd = data.DataDirHandler().jpg("composition55")
    jpeg_renderer = renderer.JpegRenderer(jd)

    coll = path.PathCollection(rec.resolution)

    xoffset = 142.5
    yoffset = 147

    xmaxsize = 2111.85
    ymaxsize = 1452

    start = (xoffset, yoffset)
    end = (xmaxsize, yoffset)

    startbottom = (xoffset, ymaxsize + yoffset)
    endbottom = (xmaxsize, ymaxsize + yoffset)

    # xspacing = 2.5

    lines = 800
    # while coll.bb()[2] < 2138:
    for i in range(lines):
        perc = (1.0 / lines) * i
        interped = p0.interp(p1, perc)
        currstartx = path.Path.mix(start[0], end[0], perc)
        currstarty = path.Path.mix(start[1], end[1], perc)
        currendx = path.Path.mix(startbottom[0], endbottom[0], perc)
        currendy = path.Path.mix(startbottom[1], endbottom[1], perc)

        curr_start = (currstartx, currstarty)
        curr_end = (currendx, currendy)
        morphed = interped.morph(curr_start, curr_end)
        coll.add(morphed, rec.resolution)

    print(coll.bb())

    gcode_renderer.render(coll, f"composition55_special_{offset}")
    try:
        jpeg_renderer.render(coll, f"composition55_special_{offset}_high2", 5.0)
    except MemoryError as me:
        print("Memory error ignored.. " + me)
        return


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=5)
    rec = ll.single(0)
    all_paths = ll.all_paths()

    entropy_filter = filter.EntropyFilter(1.5, 1.5)
    all_paths.filter(entropy_filter)

    # import random

    r1 = 25
    p0 = all_paths[r1]
    p1 = all_paths[r1 + 1]
    composition55(p0, p1, r1)

    # print(len(all_paths))
    # for i in range(10):
    #    print(F"Creating Composition #55 with offset={i}")
    #    r1 = random.randint(0, len(all_paths))
    #    p0 = all_paths[r1]
    #    p1 = all_paths[r1 +1]
    #    composition55(p0, p1, r1)
