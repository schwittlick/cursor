from cursor.collection import Collection
from cursor.renderer.hpgl import HPGLRenderer


def test_hpglrenderer():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])

    hpgl_data = HPGLRenderer.generate_string(pc)

    expected_result = "IN;PA-10,-10;PD;PA-10,-10;PA10,-10;PU;PA10,-10;PD;PA10,-10;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result


def test_hpglrenderer_pen_select():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])
    pc[0].pen_select = 1
    pc[1].pen_select = 2

    hpgl_data = HPGLRenderer.generate_string(pc)

    expected_result = "IN;SP1;PA-10,-10;PD;PA-10,-10;PA10,-10;PU;SP2;PA10,-10;PD;PA10,-10;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result
