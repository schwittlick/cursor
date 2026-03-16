from cursor.collection import Collection
from cursor.device import MinmaxMapping, PlotterType
from cursor.export import ExportWrapper
from cursor.path import Path


def main():
    plotter = PlotterType.HP_DM_SX_A1
    bb = MinmaxMapping.maps[plotter]

    x_min = bb.x
    x_max = bb.x2
    y_min = bb.y
    y_max = bb.y2
    width = x_max - x_min

    n = 10
    pc = Collection()

    for i in range(n):
        t = i / (n - 1)  # 0.0 at first line, 1.0 at last
        y = y_min + t * (y_max - y_min)

        # gradient: first line reaches x_max, last line reaches x_min + 10% of width
        x_end = x_min + (1.0 - t * 0.9) * width

        p = Path()
        p.add(x_end, y)
        p.add(x_min, y)
        pc.add(p)

    wrapper = ExportWrapper(pc, plotter, 0, "ink_smear_test", "v1")
    wrapper.ex()


if __name__ == "__main__":
    main()
