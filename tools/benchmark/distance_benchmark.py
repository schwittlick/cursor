import random

import numpy as np
import logging

from cursor.collection import Collection
from cursor.misc import distance_numba
from scipy import spatial
from cursor.misc import calc_distance
from cursor.path import Path
from cursor.timer import Timer

if __name__ == "__main__":

    collection = Collection()
    for _ in range(10000):
        collection.add(
            Path.from_tuple_list(
                [
                    (random.uniform(-10, 10), random.uniform(-10, 10)),
                    (random.uniform(-10, 10), random.uniform(-10, 10)),
                ]
            )
        )

    start_positions_float = np.array([pa.start_pos().as_tuple() for pa in collection])
    end_positions_float = np.array([pa.end_pos().as_tuple() for pa in collection])

    start_positions = np.array(
        [tuple(map(int, pa.start_pos().as_tuple())) for pa in collection]
    )
    end_positions = np.array(
        [tuple(map(int, pa.end_pos().as_tuple())) for pa in collection]
    )

    timer = Timer()
    dists = distance_numba(start_positions_float)
    #logging.info(dists)
    timer.print_elapsed("distance_numba")

    timer.start()
    distance_matrix = spatial.distance.cdist(
        end_positions_float, start_positions_float, metric="euclidean"
    )
    #int_dists = distance_matrix.astype(int)
    timer.print_elapsed("scipy.cdist")

    timer.start()
    dists = calc_distance(start_positions_float, end_positions_float)
    timer.print_elapsed("calc_distance")
