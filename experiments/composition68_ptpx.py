from cursor import device
from cursor import path
from cursor import misc


def one_card(lt):
    pc = path.PathCollection()

    count = 160
    for v in range(count):
        pa = path.Path(line_type=lt)
        pa.add(0, v)
        pa.add(10, v)
        pc.add(pa)

    return pc


def make_mapping(pc):
    mapping = {}
    for v in range(20):
        mapping[v] = f"2,{v+1}"
    return mapping


if __name__ == "__main__":
    pc = path.PathCollection()

    for lt in range(0, 16):
        x = lt % 4
        y = (lt - x) / 4
        card = one_card(lt + 2)
        card.translate(x * 15, y * 180)
        pc = pc + card

    device.SimpleExportWrapper().ex(
        pc,
        device.PlotterType.ROLAND_PNC1000,
        device.PaperSize.PORTRAIT_50_80,
        20,
        "composition68_pptx",
        f"c68_{pc.hash()}",
        # hpgl_linetype_mapping=make_mapping(pc)
    )
