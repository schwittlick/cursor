from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.renderer.svg import SvgRenderer


def test_svgrenderer():
    pc = Collection()
    p1 = Path()
    p1.add(0, 0)
    p1.add(1, 0)
    p2 = Path()
    p2.add(0, 1)
    p2.add(1, 1)

    pc.add(p1)
    pc.add(p2)

    r = SvgRenderer(DataDirHandler().test_svgs())
    r.render(pc)
    r.save("test1")
