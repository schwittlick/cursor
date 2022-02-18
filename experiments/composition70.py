from cursor import device
from cursor import path
from cursor import misc

import composition59

import random
import math
import git

if __name__ == "__main__":
    pc = path.PathCollection()
    pp = path.Path()
    composition59.full_spiral(pp, 20001, 0.0005, 0.1)
    pc.add(pp)

    bb = pc.bb()
    bbs = bb.subdiv(9, 5)

    offsets = []
    howmuch = math.radians(30)
    for _bb in bbs:
        offsets.append(random.uniform(-howmuch, howmuch))

    paths = []

    for _bb in range(len(bbs)):
        p = path.Path()
        if _bb % 2:
            p.pen_select = 1
        else:
            p.pen_select = 2

        paths.append(p)

    raender = path.Path()

    for p in pp:
        for _bb in range(len(bbs)):
            if bbs[_bb].inside(p):
                offset = offsets[_bb]
                p.rot(offset, bbs[_bb].center())
                paths[_bb].vertices.append(p)
                break

        raender.vertices.append(p)
        raender.vertices.append(p)

    pc_final = path.PathCollection()
    #pc_final.add(raender)

    for _bb in bbs:
        pc_final.add(_bb)

    for p in paths:
        pc_final.add(p)

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_DPX3300,
        device.PaperSize.LANDSCAPE_A1,
        30,
        "composition70",
        f"c70_{pc.hash()}_{sha}_6",
    )
