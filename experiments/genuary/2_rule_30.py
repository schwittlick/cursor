from cursor import loader
from cursor import data
from cursor import device
from cursor import path
from cursor import renderer
from cursor import filter


def save_wrapper(pc, projname, fname):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = renderer.JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=4.0, thickness=3)
    jpeg_renderer.save(fname)


def makepath(x, y):

    p = path.Path()
    p.add(x, y)
    p.add(x + 1, y)
    p.add(x + 1, y + 1)
    p.add(x, y + 1)
    p.add(x, y)
    return p


if __name__ == "__main__":
    leny = 150

    values = [[]]

    for _ in range(leny):
        values[0].append(0)

    values[0].append(1)

    for _ in range(leny):
        values[0].append(0)

    rules = {
        (1, 1, 1): 0,
        (1, 1, 0): 0,
        (1, 0, 1): 0,
        (1, 0, 0): 1,
        (0, 1, 1): 1,
        (0, 1, 0): 1,
        (0, 0, 1): 1,
        (0, 0, 0): 0,
    }

    for y in range(leny):
        newvalues = []
        tupleft = (values[y][len(values[y]) - 1], values[y][0], values[y][1])
        newleft = rules[tupleft]
        newvalues.append(newleft)

        for i in range(1, len(values[y]) - 1):
            tup = (values[y][i - 1], values[y][i], values[y][i + 1])
            newvalues.append(rules[tup])

        tupright = (
            values[y][len(values[y]) - 2],
            values[y][len(values[y]) - 1],
            values[y][0],
        )
        newright = rules[tupright]
        newvalues.append(newright)
        values.append(newvalues)

    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p)
    colls = ll.all_paths()
    fil = filter.EntropyMaxFilter(2.0, 2.0)
    colls.filter(fil)

    fil2 = filter.EntropyMinFilter(1.0, 1.0)
    colls.filter(fil2)
    c = path.PathCollection()

    for y in range(1, len(values)):
        for x in range(len(values[0])):
            if values[y][x]:
                # current is on, lets check from where its coming
                pr = colls.random()
                try:
                    if values[y - 1][x - 1]:
                        mor = pr.morph((x - 1, y - 1), (x, y))
                        # p = path.Path()
                        # p.add(x-1, y-1)
                        # p.add(x,y)
                        # c.add(p)
                        c.add(mor)
                except IndexError:
                    pass
                if values[y - 1][x]:
                    mor = pr.morph((x, y - 1), (x, y))

                    c.add(mor)
                try:
                    if values[y - 1][x + 1]:
                        mor = pr.morph((x + 1, y - 1), (x, y))
                        c.add(mor)
                except IndexError:
                    pass

    yv = 1
    for y in values[1:]:
        xv = 0
        for x in y:
            if x:
                pass
                # if values[yv-1][xv]
                # c.add(makepath(xv * 1, yv * 1))
            xv += 1

        yv += 1

    c.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=40)
    save_wrapper(c, "genuary", "2_rule30")
