from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.renderer import HPGLRenderer


def test_hpglrenderer():
    pc = Collection()
    p1 = Path()
    p1.add(-10, -10)
    p1.add(10, -10)

    p2 = Path()
    p2.add(10, -10)
    p2.add(10, 10)

    pc.add(p1)
    pc.add(p2)

    r = HPGLRenderer(DataDirHandler().test_hpgls())
    r.render(pc)
    hpgl_data = r.generate_string()

    expected_result = "PU;SP1;PA-10,-10;PD;PA-10,-10;PA10,-10;PU;PA10,-10;PD;PA10,-10;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result
