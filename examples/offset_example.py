import arcade.color
import random

from cursor.collection import Collection
from cursor.path import Path
from cursor.renderer import RealtimeRenderer


def add_two(r: RealtimeRenderer):
    r.clear_list()
    p = Path()

    for i in range(5):
        p.add(random.random(), random.random())

    new = p.parallel_offset(0.1)

    even_more_new = []
    for pa in new:
        new2 = pa.parallel_offset(0.1)
        for _new in new2:
            even_more_new.append(_new)

    c = Collection()
    c.add(p)
    if len(new) > 0:
        c.add(new[0])
    if len(even_more_new) > 0:
        c.add(even_more_new[0])
    c.fit((1920, 1080), padding_mm=100, keep_aspect=True)

    r.add_path(c[0], 10, arcade.color.CHERRY)
    for _c in c[1:]:
        r.add_path(_c)


def add_ten(r: RealtimeRenderer):
    r.clear_list()
    r.background(random.choice(r.colors))
    p = Path()

    for i in range(15):
        p.add(random.random(), random.random())

    c = Collection()
    c.add(p)

    for i in range(20):
        new = p.parallel_offset(0.01 * i)
        new_neg = p.parallel_offset(-0.01 * i)
        for n in new:
            c.add(n)
        for n in new_neg:
            c.add(n)

    c.fit((1920, 1080), padding_mm=100, keep_aspect=True)

    r.add_path(c[0], 10, arcade.color.BLACK)
    for _c in c[2:]:
        r.add_path(_c, 4)


if __name__ == "__main__":
    r = RealtimeRenderer(1920, 1080, "")
    r.add_cb(arcade.key.R, add_two, False)
    r.add_cb(arcade.key.KEY_5, add_ten, False)

    RealtimeRenderer.run()
