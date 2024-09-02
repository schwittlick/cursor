from cursor.collection import Collection
from cursor.path import Path
from cursor.renderer.tektronix import TektronixRenderer
from cursor.tests.fixture import get_test_hpgl_folder


def test_tektronix_renderer():
    p0 = Path()
    p0.add(0, 0)
    p0.add(1, 0)
    p0.add(2, 0)
    p0.add(3, 0)
    p0.add(4, 0)

    p1 = Path()
    p1.add(2, 2)
    p1.add(2, 3)
    p1.add(2, 4)
    p1.add(2, 5)
    p1.add(2, 6)

    pc = Collection()
    pc.add(p0)
    pc.add(p1)

    renderer = TektronixRenderer(get_test_hpgl_folder())
    renderer.render(pc)
    out = renderer.save("tektronix_test01")

    assert out == "AE `` @ `` @ a` @ b` @ c` @ `` A j` @ j` @ n` @ ba @ fa @ ja @"
