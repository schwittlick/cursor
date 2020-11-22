from cursor import loader
from cursor import renderer
from cursor import filter
from cursor import path
from cursor import data
from cursor import device


def composition37(p0, p1, offset):
    coll = path.PathCollection()
    folder = data.DataDirHandler().jpg("composition37")
    jpeg_renderer = renderer.JpegRenderer(folder)
    start = (100, 100)
    end = (100, 700)

    startbottom = (400, 100)
    endbottom = (400, 700)

    toppath = p0.morph(start, end)
    bottompath = p0.morph(endbottom, startbottom)

    bottompath.reverse()

    coll.add(toppath)
    coll.add(bottompath)

    p1_morphed = p1.morph(toppath[0].pos(), bottompath[0].pos())
    coll.add(p1_morphed)

    for i in range(len(toppath)):
        st = toppath[i]
        en = bottompath[i]
        newpath = p1.morph(en.pos(), st.pos())
        coll.add(newpath)

    print(coll.bb())

    coll.fit(
        device.RolandDPX3300.Paper.custom_30_30(),
        machine=device.RolandDPX3300(),
        padding_mm=50,
        center_point=(-880, 600),
    )
    fname = f"composition37_dpx3300_{offset}"

    hpgl_folder = data.DataDirHandler().hpgl("composition37")
    hpgl_renderer = renderer.HPGLRenderer(hpgl_folder)

    jpeg_renderer.render(coll)
    jpeg_renderer.save(fname)

    separate_layers = coll.get_layers()
    for layer, pc in separate_layers.items():
        hpgl_renderer.render(pc)
        hpgl_renderer.save(f"{fname}_{layer}")


if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=15)
    all_paths = ll.all_paths()

    entropy_filter = filter.EntropyMinFilter(2.5, 2.5)
    all_paths.filter(entropy_filter)

    mincount_filter = filter.MinPointCountFilter(20)
    all_paths.filter(mincount_filter)

    maxcount_filter = filter.MaxPointCountFilter(100)
    all_paths.filter(maxcount_filter)

    for i in range(10):
        import random

        r = random.randint(0, len(all_paths) - 1)
        print(f"Creating Composition #37 with offset={r}")
        p0 = all_paths[r]
        p1 = all_paths[r + 1]
        composition37(p0, p1, i)
