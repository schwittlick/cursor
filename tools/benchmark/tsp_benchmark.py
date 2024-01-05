import logging

from cursor.collection import Collection
from cursor.path import Path

import random

if __name__ == "__main__":
    collection = Collection()
    for _ in range(10000):
        collection.add(
            Path.from_tuple_list(
                [(random.uniform(-100, 100), random.uniform(-100, 100))]
            )
        )
    collection.fast_tsp(plot_preview=True, duration_seconds=1)
    travel = collection.calc_travel_distance(40)
    logging.info(f"Total dist: {travel}")
