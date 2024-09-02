from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.renderer.digi import DigiplotRenderer
from cursor.tests.fixture import get_test_hpgl_folder


def test_digiplot_renderer():
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

    renderer = DigiplotRenderer(get_test_hpgl_folder())
    renderer.render(pc)
    out = renderer.save("digi_test01")

    assert (
        out == "X,0;/Y,0;H;K;X,0;/Y,0;I;K;X,1;/Y,0;I;K;X,2"
        ";/Y,0;I;K;X,3;/Y,0;I;K;X,4;/Y,0;I;K;X,2;/Y,"
        "2;H;K;X,2;/Y,2;I;K;X,2;/Y,3;I;K;X,2;/Y,4;I;K"
        ";X,2;/Y,5;I;K;X,2;/Y,6;I;K;X,0;/Y,0;H;K;"
    )
