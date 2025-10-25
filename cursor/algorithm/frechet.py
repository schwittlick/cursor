import math
from multiprocessing import Manager, Process
from typing import Callable

import numpy as np


def euclidean(p: np.ndarray, q: np.ndarray) -> float:
    d = p - q
    return math.sqrt(np.dot(d, d))


def parallel_function(paths, out_array, idx, reference_path):
    ll = [(index, item.frechet_similarity(reference_path), item) for index, item in enumerate(paths)]
    out_array[idx] = ll


def frechet_multiprocessing(paths: list, reference_path):
    cpus = 4  # os.cpu_count()

    def chunks(a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))

    paths_chunked = list(chunks(paths, cpus))

    distances = []
    with Manager() as manager:
        shared_list = manager.list(range(cpus))
        processes = []

        for i in range(cpus):
            p = Process(
                target=parallel_function,
                args=(paths_chunked[i], shared_list, i, reference_path),
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        for i in shared_list:
            for distance in i:
                distances.append(distance)

        return distances


class DiscreteFrechet(object):
    """
    Calculates the discrete Fréchet distance between two poly-lines using the
    original recursive algorithm
    """

    def __init__(self, dist_func):
        """
        Initializes the instance with a pairwise distance function.
        :param dist_func: The distance function. It must accept two NumPy
        arrays containing the point coordinates (x, y), (lat, long)
        """
        self.dist_func = dist_func
        self.ca = np.array([0.0])

    def distance(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        Calculates the Fréchet distance between poly-lines p and q
        This function implements the algorithm described by Eiter & Mannila
        :param p: Poly-line p
        :param q: Poly-line q
        :return: Distance value
        """

        def calculate(i: int, j: int) -> float:
            """
            Calculates the distance between p[i] and q[i]
            :param i: Index into poly-line p
            :param j: Index into poly-line q
            :return: Distance value
            """
            if self.ca[i, j] > -1.0:
                return self.ca[i, j]

            d = self.dist_func(p[i], q[j])
            if i == 0 and j == 0:
                self.ca[i, j] = d
            elif i > 0 and j == 0:
                self.ca[i, j] = max(calculate(i - 1, 0), d)
            elif i == 0 and j > 0:
                self.ca[i, j] = max(calculate(0, j - 1), d)
            elif i > 0 and j > 0:
                self.ca[i, j] = max(
                    min(
                        calculate(i - 1, j),
                        calculate(i - 1, j - 1),
                        calculate(i, j - 1),
                    ),
                    d,
                )
            else:
                self.ca[i, j] = np.inf
            return self.ca[i, j]

        n_p = p.shape[0]
        n_q = q.shape[0]
        self.ca = np.zeros((n_p, n_q))
        self.ca.fill(-1.0)
        return calculate(n_p - 1, n_q - 1)


def _get_linear_frechet(
    p: np.ndarray, q: np.ndarray, dist_func: Callable[[np.ndarray, np.ndarray], float]
) -> np.ndarray:
    n_p = p.shape[0]
    n_q = q.shape[0]
    ca = np.zeros((n_p, n_q), dtype=np.float64)

    for i in range(n_p):
        for j in range(n_q):
            d = dist_func(p[i], q[j])

            if i > 0 and j > 0:
                ca[i, j] = max(min(ca[i - 1, j], ca[i - 1, j - 1], ca[i, j - 1]), d)
            elif i > 0 and j == 0:
                ca[i, j] = max(ca[i - 1, 0], d)
            elif i == 0 and j > 0:
                ca[i, j] = max(ca[0, j - 1], d)
            elif i == 0 and j == 0:
                ca[i, j] = d
            else:
                ca[i, j] = np.inf
    return ca


class LinearDiscreteFrechet(DiscreteFrechet):
    def __init__(self, dist_func):
        DiscreteFrechet.__init__(self, dist_func)
        # JIT the numba code
        self.distance(np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0.0, 0.0], [1.0, 1.0]]))

    def distance(self, p: np.ndarray, q: np.ndarray) -> float:
        n_p = p.shape[0]
        n_q = q.shape[0]
        self.ca = _get_linear_frechet(p, q, self.dist_func)
        return self.ca[n_p - 1, n_q - 1]
