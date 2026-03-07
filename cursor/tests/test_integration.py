from cursor import device
from cursor.collection import Collection
from cursor.export import ExportWrapper
from cursor.path import Path


def test_exporter():
    pc = Collection()

    p = Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)
    pc.add(p)

    wrapper = ExportWrapper(
        pc,
        device.PlotterType.HP_7550A_A3,
        30,
        "simple_rect_example",
        "simple_rect",
    )
    wrapper.fit()
    wrapper.ex()
