from cursor import device
from cursor import export
from cursor import path
from cursor import collection

import pytest


@pytest.mark.skip(reason="This is not really a test at the moment.")
def test_simple_export():
    p = path.Path()
    p.add(3, 5)
    p.add(5, 9)
    p.add(-3, -10)

    pc = collection.Collection()
    pc.add(p)

    cfg = export.ExportConfig()
    cfg.type = device.PlotterType.ROLAND_DPX3300_A1
    cfg.dimension = device.PaperSize.LANDSCAPE_A1
    cfg.margin = 90

    exp = export.Exporter()
    exp.cfg = cfg
    exp.collection = pc
    exp.name = "composition59"
    exp.suffix = "test_full_spiral_test"
    exp.run(True)
