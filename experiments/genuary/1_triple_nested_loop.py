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

    jpeg_renderer.render(pc, scale=1.0)
    jpeg_renderer.save(fname)


def genuary1(seed):

    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)
    colls = ll.all_paths()

    c = path.PathCollection()
    counter = 0
    for z in range(3):
        for y in range(3):
            for x in range(3):
                n = counter
                print(n)
                min_filter = filter.MinPointCountFilter(n)
                colls.filter(min_filter)
                p1 = colls.random()
                p2 = p1.morph((counter, counter), (counter, counter + 100))

                c.add(p2)

                counter += 10

    c.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=90)
    save_wrapper(c, "genuary", f"1_triple_nested_loop_seed{seed}")


if __name__ == "__main__":
    for _ in range(10):
        random.seed(_)
        genuary1(_)