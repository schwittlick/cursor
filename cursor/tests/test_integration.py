from cursor.collection import Collection
from cursor.path import Path
from cursor.export import ExportWrapper
from cursor import device


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
        device.PlotterType.HP_DM_RX_PLUS_A2,
        30,
        "simple_rect_example",
        "simple_rect", )
    wrapper.fit()
    wrapper.ex()
