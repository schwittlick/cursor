from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property
from cursor.renderer.svg import SvgRenderer


def test_svgrenderer():
    pc = Collection()
    p1 = Path.from_tuple_list([(0, 0), (10, 10)])
    p1.properties[Property.COLOR] = (255, 0, 0)
    p1.properties[Property.WIDTH] = 0.2
    p2 = Path.from_tuple_list([(10, 0), (0, 10)])
    p2.properties[Property.COLOR] = (0, 255, 0)
    p2.properties[Property.WIDTH] = 0.2

    pc.add(p1)
    pc.add(p2)

    pos1 = Position(0.5, 5)
    pos1.properties[Property.COLOR] = (255, 0, 255)
    pos1.properties[Property.WIDTH] = 0.1

    pos2 = Position(9.5, 5)
    pos2.properties[Property.COLOR] = (0, 255, 255)
    pos2.properties[Property.WIDTH] = 0.1

    r = SvgRenderer(DataDirHandler().test_svgs(), 10, 10)
    r.add(pc)
    r.add([pos1, pos2])
    r.render()
    r.save("test1")
