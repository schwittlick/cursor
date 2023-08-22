from cursor.renderer.hpgl import HPGLRenderer
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.collection import Collection

if __name__ == "__main__":
    pc = Collection()

    p = Path()
    p.add(0, 0)
    p.add(1000, 0)
    p.add(1000, 1000)
    p.add(0, 1000)
    p.add(0, 0)

    pc.add(p)

    hpgl_folder = DataDirHandler().hpgl("example_raw_hpgl")
    hpgl_renderer = HPGLRenderer(hpgl_folder)
    hpgl_renderer.render(pc)
    hpgl_str = hpgl_renderer.save("example_raw_hpgl")
