from cursor.path import Path, PathCollection
from cursor.misc import map

import numpy as np


def img_to_path(img, lines: int = 660):
    """
    This works only for A3 on HP7579a
    Mit dem neuen zentrierungs-Mechanismus haben wir 33cm in der Höhe
    Mit Stiftstärke von ~0.5mm -> 660 linien
    """
    pc = PathCollection()

    rows, cols = img.shape
    for x in range(rows):
        pa = Path()
        for i in range(lines):
            line_index = int(map(i, 0, lines, 0, cols, True))
            k = img[x, line_index]
            if k == 0:
                pa.add(x, line_index)
                pa.add(x, line_index + 0.1)
                pass
            if k == 255:
                if pa.empty():
                    continue

                pa.pen_select = int(np.clip(len(pa), 0, 16) / 2)
                pc.add(pa)
                pa = Path()
                pass
    return pc
