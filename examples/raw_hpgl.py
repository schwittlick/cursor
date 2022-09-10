from cursor import data
from cursor import path
from cursor import renderer
from cursor import collection


if __name__ == "__main__":
    pc = collection.Collection()

    p = path.Path()
    p.add(0, 0)
    p.add(1000, 0)
    p.add(1000, 1000)
    p.add(0, 1000)
    p.add(0, 0)

    pc.add(p)

    hpgl_folder = data.DataDirHandler().hpgl("example_raw_hpgl")
    hpgl_renderer = renderer.HPGLRenderer(hpgl_folder)
    hpgl_renderer.render(pc)
    hpgl_str = hpgl_renderer.save("example_raw_hpgl")
