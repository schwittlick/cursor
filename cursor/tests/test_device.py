from cursor import device
from cursor import path


def test_simple_export():
    p = path.Path()
    p.add(3, 5)
    p.add(5, 9)
    p.add(-3, -10)

    pc = path.PathCollection()
    pc.add(p)

    cfg = device.Cfg()
    cfg.type = device.PlotterType.ROLAND_DPX3300
    cfg.dimension = device.PaperSize.LANDSCAPE_A1
    cfg.margin = 90

    exp = device.Exporter()
    exp.cfg = cfg
    exp.paths = pc
    exp.name = "composition59"
    exp.suffix = "test_full_spiral_test"
    exp.run(True)

