from cursor import device
from cursor import path


def gen_gradient(pen_select: int, direction: bool):
    pc = path.PathCollection()

    for i in range(100):
        p = path.Path()

        p.pen_select = pen_select
        if direction:
            p.add(0, i + 0.5)
            p.add(100, i + 0.5)
            p.velocity = 101 - (i + 1)
        else:
            p.add(0, i)
            p.add(100, i)
            p.velocity = i + 1
        pc.add(p)

    return pc


if __name__ == "__main__":
    # recordings = data.DataDirHandler().recordings()
    # _loader = loader.Loader(directory=recordings, limit_files=1)
    # pc = _loader.all_paths()

    padding = 104

    pc1 = gen_gradient(1, True)
    pc2 = gen_gradient(2, False)

    pc3 = gen_gradient(3, True)
    pc3.translate(padding, 0)
    pc4 = gen_gradient(4, False)
    pc4.translate(padding, 0)

    pc5 = gen_gradient(5, True)
    pc5.translate(padding, padding)
    pc6 = gen_gradient(6, False)
    pc6.translate(padding, padding)

    pc7 = gen_gradient(7, True)
    pc7.translate(0, padding)
    pc8 = gen_gradient(8, False)
    pc8.translate(0, padding)

    pc_final = path.PathCollection()
    pc_final = pc_final + pc1
    pc_final = pc_final + pc2
    pc_final = pc_final + pc3
    pc_final = pc_final + pc4
    pc_final = pc_final + pc5
    pc_final = pc_final + pc6
    pc_final = pc_final + pc7
    pc_final = pc_final + pc8

    device.SimpleExportWrapper().ex(
        pc_final,
        device.PlotterType.HP_7595A_A3,
        device.PaperSize.LANDSCAPE_A3,
        35,
        "genuary22_16_color_gradient",
        f"4 gradients{pc_final.hash()}",
    )
