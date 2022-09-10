from cursor.path import Path, PathCollection
from cursor.misc import map

import numpy as np
from PIL import Image

# add svg2cursor
# add img2cursor


def print_statistics(pc: PathCollection):
    selects = [0, 0, 0, 0, 0, 0, 0, 0]

    for pa in pc:
        selects[pa.pen_select - 1] += 1

    print(selects)


def img_to_path(img, layers: int = 8):
    """
    This works only for A3 on HP7579a
    Mit dem neuen zentrierungs-Mechanismus haben wir 33cm in der Höhe
    Mit Stiftstärke von ~0.5mm -> 660 linien

    A1:
    35mm padding -> 52x77cm
    """
    pc = PathCollection()

    w = 77 * 2 * 10
    h = 52 * 2 * 5

    img_w, img_h = img.size
    if img_w < img_h:
        print("transposing")
        img = img.transpose(Image.ROTATE_90)

    img = img.resize((w, h))
    img = img.convert("1")

    lens = []
    for x in range(w):
        pa = Path()
        start = img.getpixel((0, 0))
        curr = start
        for y in range(h):
            # xpos = int(map(x, 0, w, 0, img_w, False))
            # ypos = int(map(y, 0, h, 0, img_h, False))
            v = img.getpixel((x, y))
            _y = float(y)
            _x = float(x)
            if v == curr:
                pa.add(_x, _y)
            else:
                curr = v
                if pa.empty():
                    continue

                lens.append(len(pa))
                pc.add(pa)
                pa = Path()
                pa.add(_x, _y)
        if pa.empty():
            continue
        pc.add(pa)

    max_len = max(lens)
    print(f"max len:{max_len}")

    fin_pc = PathCollection()
    for pa in pc:
        new_pa = Path()
        new_pa.add(pa.start_pos().x, pa.start_pos().y)
        new_pa.add(pa.end_pos().x, pa.end_pos().y)
        new_pa.pen_select = int(
            map(np.clip(len(pa), 0, max_len), 0, max_len / 1, 1, 8, False)
        )
        # ps = int(map(len(pa), 0, max_len, 0, layers, False))
        # new_pa.layer = ps
        new_pa.velocity = 10

        if len(pa) > 1:
            fin_pc.add(new_pa)
        else:
            print(f"ignoring path with layer {pa.layer}")

    print_statistics(fin_pc)
    return fin_pc

    prev = None
    buffered = None
    layers = fin_pc.get_layers()
    pc_combined = PathCollection()
    for layer in layers.values():
        for pa in layer:
            if prev is not None:
                if buffered is None:
                    buffered = prev.copy()
                    buffered.pen_select = prev.pen_select

                if (
                    prev.end_pos().x == pa.start_pos().x
                    and prev.end_pos().y + 1 == pa.start_pos().y
                ):
                    buffered.add(pa.start_pos().x, pa.start_pos().y)
                else:
                    buffered_simple = Path()
                    buffered_simple.velocity = 10
                    buffered_simple.pen_select = buffered.pen_select
                    buffered_simple.add(buffered.start_pos().x, buffered.start_pos().y)
                    buffered_simple.add(buffered.end_pos().x, buffered.end_pos().y)
                    pc_combined.add(buffered_simple)
                    buffered = None
            else:
                pc_combined.add(pa)
            prev = pa

    print_statistics(pc_combined)

    return pc_combined
