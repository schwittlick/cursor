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


def test_hpglrenderer_acceleration():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)]])

    hpgl_data = HPGLRenderer.generate_string(pc, auto_pen_ops=11, acceleration=1)

    assert hpgl_data == "IN;AP11;AS1;SP1;PA-10,-10;PD;PA10,-10;PU;PA0,0;SP0;"
    assert HPGLRenderer.generate_string(pc, acceleration=2).startswith("IN;AS2;SP1;")


def test_hpglrenderer_acceleration_per_path_and_travel():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])
    pc[0].acceleration = 4
    pc[1].acceleration = 4

    hpgl_data = HPGLRenderer.generate_string(pc, travel_acceleration=1)

    assert hpgl_data == "IN;SP1;AS1;PA-10,-10;AS4;PD;PA10,-10;PU;AS1;PA10,-10;AS4;PD;PA10,10;PU;AS1;PA0,0;SP0;"


def test_hpglrenderer_acceleration_only_when_changed():
    pc = Collection.from_tuples([[(-10, -10), (10, -10)], [(10, -10), (10, 10)]])
    pc[0].acceleration = 2
    pc[1].acceleration = 2

    hpgl_data = HPGLRenderer.generate_string(pc, acceleration=4)

    assert hpgl_data == "IN;AS4;SP1;PA-10,-10;AS2;PD;PA10,-10;PU;PA10,-10;PD;PA10,10;PU;PA0,0;SP0;"
