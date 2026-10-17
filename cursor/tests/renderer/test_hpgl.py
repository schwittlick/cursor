from cursor.collection import Collection
from cursor.hpgl import AP_DEFAULT, AP_LIFT_IDLE, AP_MERGE_PEN_UP, AP_STORE_IDLE
from cursor.renderer.hpgl import HPGLRenderer


def test_hpglrenderer():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])

    hpgl_data = HPGLRenderer.generate_string(pc)

    expected_result = "IN;SP1;PA-10,-10;PD;PA10,-10;PU;PA10,-10;PD;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result


def test_hpglrenderer_pen_select():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])
    pc[0].pen_select = 1
    pc[1].pen_select = 2

    hpgl_data = HPGLRenderer.generate_string(pc)

    expected_result = "IN;SP1;PA-10,-10;PD;PA10,-10;PU;SP2;PA10,-10;PD;PA10,10;PU;PA0,0;SP0;"
    assert hpgl_data == expected_result


def test_hpglrenderer_auto_pen_ops():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)]])

    assert AP_DEFAULT == 95
    ops = AP_LIFT_IDLE | AP_STORE_IDLE | AP_MERGE_PEN_UP

    hpgl_data = HPGLRenderer.generate_string(pc, auto_pen_ops=ops)

    assert hpgl_data == "IN;AP11;SP1;PA-10,-10;PD;PA10,-10;PU;PA0,0;SP0;"
    assert HPGLRenderer.generate_string(pc).startswith("IN;SP1;")
