from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.renderer.hpgl import HPGLRenderer


def test_hpglrenderer():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])

    r = HPGLRenderer(DataDirHandler().test_hpgls())
    r.add(pc)
    hpgl_data = r.generate_string()

    expected_result = "PU;PA-10,-10;PD;PA-10,-10;PA10,-10;PU;PA10,-10;PD;PA10,-10;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result


def test_hpglrenderer_pen_select():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])
    pc[0].pen_select = 1
    pc[1].pen_select = 2

    r = HPGLRenderer(DataDirHandler().test_hpgls())
    r.add(pc)
    hpgl_data = r.generate_string()

    expected_result = "PU;SP1;PA-10,-10;PD;PA-10,-10;PA10,-10;PU;SP2;PA10,-10;PD;PA10,-10;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result
