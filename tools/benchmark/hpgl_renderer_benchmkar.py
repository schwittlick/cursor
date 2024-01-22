import pathlib

from cursor.collection import Collection
from cursor.path import Path

import random

# import cProfile as profile
# import pstats

from cursor.renderer.hpgl import HPGLRenderer

if __name__ == "__main__":
    collection = Collection()
    for _ in range(100000):
        pa = Path.from_tuple_list(
            [(random.uniform(-100, 100), random.uniform(-100, 100))]
        )
        pa.pen_select = int(random.uniform(1, 8))
        pa.velocity = int(random.uniform(1, 120))
        pa.pen_force = int(random.uniform(1, 8))
        collection.add(pa)

    # profile.runctx("renderer.generate_string()", globals(), locals(), filename="profile_results")
    # stats = pstats.Stats("profile_results")
    # stats.sort_stats("time").print_stats()
    hpgl_str = HPGLRenderer.generate_string(collection)  # 575ms
    # logging.info(hpgl_str)
