import time
import numpy as np
import inspect
import math
import pynput
from typing import Callable, Dict
from numba import jit, types, int32, int64
from numba import typed
from timeit import default_timer as timer


def mix(begin: float, end: float, perc: float):
    return ((end - begin) * perc) + begin


def entropy2(labels: list, base=None) -> float:
    from math import log, e

    """ Computes entropy of label distribution. """

    n_labels = len(labels)

    if n_labels <= 1:
        return 0

    value, counts = np.unique(labels, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.0

    # Compute entropy
    base = e if base is None else base
    for i in probs:
        ent -= i * log(i, base)

    return ent


class Timer:
    def __init__(self):
        self._time = None

    def start(self):
        self._time = time.perf_counter()

    def elapsed(self):
        return time.perf_counter() - self._time

    def print_elapsed(self):
        print(self.elapsed())


def convert_pynput_btn_to_key(btn):
    """
    these keyboard keys dont have char representation
    we make it ourselves
    """
    if btn == pynput.keyboard.Key.space:
        return " "

    if btn == pynput.keyboard.Key.delete:
        return "DEL"

    if btn == pynput.keyboard.Key.cmd:
        return "CMD"

    if btn == pynput.keyboard.Key.cmd_l:
        return "CMD_L"

    if btn == pynput.keyboard.Key.cmd_r:
        return "CMD_R"

    if btn == pynput.keyboard.Key.alt:
        return "ALT"

    if btn == pynput.keyboard.Key.alt_l:
        return "ALT_L"

    if btn == pynput.keyboard.Key.alt_r:
        return "ALT_R"

    if btn == pynput.keyboard.Key.enter:
        return "ENTER"

    if btn == pynput.keyboard.Key.backspace:
        return "BACKSPACE"

    if btn == pynput.keyboard.Key.shift:
        return "SHIFT"

    if btn == pynput.keyboard.Key.shift_l:
        return "SHIFT_L"

    if btn == pynput.keyboard.Key.shift_r:
        return "SHIFT_R"

    if btn == pynput.keyboard.Key.ctrl:
        return "CTRL"

    if btn == pynput.keyboard.Key.ctrl_l:
        return "CTRL_L"

    if btn == pynput.keyboard.Key.ctrl_r:
        return "CTRL_R"

    return None


def generate_perlin_noise_2d(shape, res):
    def f(t):
        return 6 * t**5 - 15 * t**4 + 10 * t**3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0 : res[0] : delta[0], 0 : res[1] : delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
    # Interpolation
    t = f(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)


def map(value, inputMin, inputMax, outputMin, outputMax, clamp):
    outVal = (value - inputMin) / (inputMax - inputMin) * (
        outputMax - outputMin
    ) + outputMin

    if clamp:
        if outputMax < outputMin:
            if outVal < outputMax:
                outVal = outputMax
            elif outVal > outputMin:
                outVal = outputMin
    else:
        if outVal > outputMax:
            outVal = outputMax
        elif outVal < outputMin:
            outVal = outputMin
    return outVal


def current_source(frame):
    return inspect.getsource(inspect.getmodule(frame))


def _c(ca, i, j, p, q):

    if ca[i, j] > -1:
        return ca[i, j]
    elif i == 0 and j == 0:
        ca[i, j] = np.linalg.norm(p[i] - q[j])
    elif i > 0 and j == 0:
        ca[i, j] = max(_c(ca, i - 1, 0, p, q), np.linalg.norm(p[i] - q[j]))
    elif i == 0 and j > 0:
        ca[i, j] = max(_c(ca, 0, j - 1, p, q), np.linalg.norm(p[i] - q[j]))
    elif i > 0 and j > 0:
        ca[i, j] = max(
            min(
                _c(ca, i - 1, j, p, q),
                _c(ca, i - 1, j - 1, p, q),
                _c(ca, i, j - 1, p, q),
            ),
            np.linalg.norm(p[i] - q[j]),
        )
    else:
        ca[i, j] = float("inf")

    return ca[i, j]


def frdist(p, q):
    """
    Computes the discrete Fréchet distance between
    two curves. The Fréchet distance between two curves in a
    metric space is a measure of the similarity between the curves.
    The discrete Fréchet distance may be used for approximately computing
    the Fréchet distance between two arbitrary curves,
    as an alternative to using the exact Fréchet distance between a polygonal
    approximation of the curves or an approximation of this value.
    This is a Python 3.* implementation of the algorithm produced
    in Eiter, T. and Mannila, H., 1994. Computing discrete Fréchet distance.
    Tech. Report CD-TR 94/64, Information Systems Department, Technical
    University of Vienna.
    http://www.kr.tuwien.ac.at/staff/eiter/et-archive/cdtr9464.pdf
    Function dF(P, Q): real;
        input: polygonal curves P = (u1, . . . , up) and Q = (v1, . . . , vq).
        return: δdF (P, Q)
        ca : array [1..p, 1..q] of real;
        function c(i, j): real;
            begin
                if ca(i, j) > −1 then return ca(i, j)
                elsif i = 1 and j = 1 then ca(i, j) := d(u1, v1)
                elsif i > 1 and j = 1 then ca(i, j) := max{ c(i − 1, 1), d(ui, v1) }
                elsif i = 1 and j > 1 then ca(i, j) := max{ c(1, j − 1), d(u1, vj) }
                elsif i > 1 and j > 1 then ca(i, j) :=
                max{ min(c(i − 1, j), c(i − 1, j − 1), c(i, j − 1)), d(ui, vj ) }
                else ca(i, j) = ∞
                return ca(i, j);
            end; /* function c */
        begin
            for i = 1 to p do for j = 1 to q do ca(i, j) := −1.0;
            return c(p, q);
        end.
    Parameters
    ----------
    P : Input curve - two dimensional array of points
    Q : Input curve - two dimensional array of points
    Returns
    -------
    dist: float64
        The discrete Fréchet distance between curves `P` and `Q`.
    """
    p = np.array(p, np.float64)
    q = np.array(q, np.float64)

    len_p = len(p)
    len_q = len(q)

    if len_p == 0 or len_q == 0:
        raise ValueError("Input curves are empty.")

    if len_p != len_q or len(p[0]) != len(q[0]):
        raise ValueError("Input curves do not have the same dimensions.")

    ca = np.ones((len_p, len_q), dtype=np.float64) * -1

    dist = _c(ca, len_p - 1, len_q - 1, p, q)
    return dist


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
                self.ca[i, j] = np.infty
            return self.ca[i, j]

        n_p = p.shape[0]
        n_q = q.shape[0]
        self.ca = np.zeros((n_p, n_q))
        self.ca.fill(-1.0)
        return calculate(n_p - 1, n_q - 1)


@jit(nopython=True)
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
                ca[i, j] = np.infty
    return ca


class LinearDiscreteFrechet(DiscreteFrechet):
    def __init__(self, dist_func):
        DiscreteFrechet.__init__(self, dist_func)
        # JIT the numba code
        self.distance(
            np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0.0, 0.0], [1.0, 1.0]])
        )

    def distance(self, p: np.ndarray, q: np.ndarray) -> float:
        n_p = p.shape[0]
        n_q = q.shape[0]
        self.ca = _get_linear_frechet(p, q, self.dist_func)
        return self.ca[n_p - 1, n_q - 1]


@jit(nopython=True)
def distance_matrix(
    p: np.ndarray, q: np.ndarray, dist_func: Callable[[np.array, np.array], float]
) -> np.ndarray:
    n_p = p.shape[0]
    n_q = q.shape[0]
    dist = np.zeros((n_p, n_q), dtype=np.float64)
    for i in range(n_p):
        for j in range(n_q):
            dist[i, j] = dist_func(p[i], q[j])
    return dist


class VectorizedDiscreteFrechet(DiscreteFrechet):
    def __init__(self, dist_func):
        DiscreteFrechet.__init__(self, dist_func)
        self.dist = np.array([0.0])

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

            d = self.dist[i, j]
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
                self.ca[i, j] = np.infty
            return self.ca[i, j]

        n_p = p.shape[0]
        n_q = q.shape[0]
        self.ca = np.zeros((n_p, n_q))
        self.ca.fill(-1.0)
        self.dist = distance_matrix(p, q, dist_func=self.dist_func)
        return calculate(n_p - 1, n_q - 1)


@jit(nopython=True)
def _bresenham_pairs(x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    """Generates the diagonal coordinates
    Parameters
    ----------
    x0 : int
        Origin x value
    y0 : int
        Origin y value
    x1 : int
        Target x value
    y1 : int
        Target y value
    Returns
    -------
    np.ndarray
        Array with the diagonal coordinates
    """
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    dim = max(dx, dy)
    pairs = np.zeros((dim, 2), dtype=np.int64)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx // 2
        for i in range(dx):
            pairs[i, 0] = x
            pairs[i, 1] = y
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        for i in range(dy):
            pairs[i, 0] = x
            pairs[i, 1] = y
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    return pairs


@jit(int64(int32, int32), nopython=True)
def rc(row: types.int32, col: types.int32) -> types.int64:
    return (row << 32) + col


@jit(nopython=True)
def _get_rc(
    a: Dict, row: types.int64, col: types.int64, d: types.float64 = np.inf
) -> types.float64:
    kk = rc(row, col)
    if kk in a:
        return a.get(kk)
    else:
        return d


@jit(nopython=True)
def _get_corner_min_sparse(f_mat: Dict, i: int, j: int) -> float:
    if i > 0 and j > 0:
        a = min(
            _get_rc(f_mat, i - 1, j - 1),
            _get_rc(f_mat, i, j - 1),
            _get_rc(f_mat, i - 1, j),
        )
    elif i == 0 and j == 0:
        a = f_mat.get(rc(i, j))
    elif i == 0:
        a = f_mat.get(rc(i, j - 1))
    else:  # j == 0:
        a = f_mat.get(rc(i - 1, j))
    return a


@jit(nopython=True)
def _get_corner_min_array(f_mat: np.ndarray, i: int, j: int) -> float:
    if i > 0 and j > 0:
        a = min(f_mat[i - 1, j - 1], f_mat[i, j - 1], f_mat[i - 1, j])
    elif i == 0 and j == 0:
        a = f_mat[i, j]
    elif i == 0:
        a = f_mat[i, j - 1]
    else:  # j == 0:
        a = f_mat[i - 1, j]
    return a


@jit(nopython=True)
def _fast_distance_sparse(
    p: np.ndarray,
    q: np.ndarray,
    diag: np.ndarray,
    dist_func: Callable[[np.array, np.array], float],
) -> Dict:
    n_diag = diag.shape[0]
    diag_max = 0.0
    i_min = 0
    j_min = 0
    p_count = p.shape[0]
    q_count = q.shape[0]

    # Create the distance array
    dist = typed.Dict.empty(key_type=types.int64, value_type=types.float64)

    # Fill in the diagonal with the seed distance values
    for k in range(n_diag):
        i0 = diag[k, 0]
        j0 = diag[k, 1]
        d = dist_func(p[i0], q[j0])
        if d > diag_max:
            diag_max = d
        dist[rc(i0, j0)] = d

    for k in range(n_diag - 1):
        i0 = diag[k, 0]
        j0 = diag[k, 1]

        p_i0 = p[i0]
        q_j0 = q[j0]

        for i in range(i0 + 1, p_count):
            key = rc(i, j0)
            if key not in dist:
                d = dist_func(p[i], q_j0)
                if d < diag_max or i < i_min:
                    dist[key] = d
                else:
                    break
            else:
                break
        i_min = i

        for j in range(j0 + 1, q_count):
            key = rc(i0, j)
            if key not in dist:
                d = dist_func(p_i0, q[j])
                if d < diag_max or j < j_min:
                    dist[key] = d
                else:
                    break
            else:
                break
        j_min = j
    return dist


@jit(nopython=True)
def _fast_distance_matrix(p, q, diag, dist_func):
    n_diag = diag.shape[0]
    diag_max = 0.0
    i_min = 0
    j_min = 0
    p_count = p.shape[0]
    q_count = q.shape[0]

    # Create the distance array
    dist = np.full((p_count, q_count), np.inf, dtype=np.float64)

    # Fill in the diagonal with the seed distance values
    for k in range(n_diag):
        i0 = diag[k, 0]
        j0 = diag[k, 1]
        d = dist_func(p[i0], q[j0])
        diag_max = max(diag_max, d)
        dist[i0, j0] = d

    for k in range(n_diag - 1):
        i0 = diag[k, 0]
        j0 = diag[k, 1]
        p_i0 = p[i0]
        q_j0 = q[j0]

        for i in range(i0 + 1, p_count):
            if np.isinf(dist[i, j0]):
                d = dist_func(p[i], q_j0)
                if d < diag_max or i < i_min:
                    dist[i, j0] = d
                else:
                    break
            else:
                break
        i_min = i

        for j in range(j0 + 1, q_count):
            if np.isinf(dist[i0, j]):
                d = dist_func(p_i0, q[j])
                if d < diag_max or j < j_min:
                    dist[i0, j] = d
                else:
                    break
            else:
                break
        j_min = j
    return dist


@jit(nopython=True)
def _fast_frechet_sparse(dist, diag: np.ndarray, p: np.ndarray, q: np.ndarray):

    for k in range(diag.shape[0]):
        i0 = diag[k, 0]
        j0 = diag[k, 1]

        for i in range(i0, p.shape[0]):
            key = rc(i, j0)
            if key in dist:
                c = _get_corner_min_sparse(dist, i, j0)
                if c > dist[key]:
                    dist[key] = c
            else:
                break

        # Add 1 to j0 to avoid recalculating the diagonal
        for j in range(j0 + 1, q.shape[0]):
            key = rc(i0, j)
            if key in dist:
                c = _get_corner_min_sparse(dist, i0, j)
                if c > dist[key]:
                    dist[key] = c
            else:
                break
    return dist


@jit(nopython=True)
def _fast_frechet_matrix(
    dist: np.ndarray, diag: np.ndarray, p: np.ndarray, q: np.ndarray
) -> np.ndarray:

    for k in range(diag.shape[0]):
        i0 = diag[k, 0]
        j0 = diag[k, 1]

        for i in range(i0, p.shape[0]):
            if np.isfinite(dist[i, j0]):
                c = _get_corner_min_array(dist, i, j0)
                if c > dist[i, j0]:
                    dist[i, j0] = c
            else:
                break

        # Add 1 to j0 to avoid recalculating the diagonal
        for j in range(j0 + 1, q.shape[0]):
            if np.isfinite(dist[i0, j]):
                c = _get_corner_min_array(dist, i0, j)
                if c > dist[i0, j]:
                    dist[i0, j] = c
            else:
                break
    return dist


@jit(nopython=True)
def _fdfd_sparse(
    p: np.ndarray, q: np.ndarray, dist_func: Callable[[np.array, np.array], float]
) -> float:
    diagonal = _bresenham_pairs(0, 0, p.shape[0], q.shape[0])
    ca = _fast_distance_sparse(p, q, diagonal, dist_func)
    ca = _fast_frechet_sparse(ca, diagonal, p, q)
    return ca


@jit(nopython=True)
def _fdfd_matrix(
    p: np.ndarray, q: np.ndarray, dist_func: Callable[[np.array, np.array], float]
) -> float:
    diagonal = _bresenham_pairs(0, 0, p.shape[0], q.shape[0])
    ca = _fast_distance_matrix(p, q, diagonal, dist_func)
    ca = _fast_frechet_matrix(ca, diagonal, p, q)
    return ca


class FastDiscreteFrechetSparse(object):
    def __init__(self, dist_func):
        """
        Parameters
        ----------
        dist_func:
        """
        self.times = []
        self.dist_func = dist_func
        self.ca = typed.Dict.empty(key_type=types.int64, value_type=types.float64)
        # JIT the numba code
        self.distance(
            np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0.0, 0.0], [1.0, 1.0]])
        )

    def timed_distance(self, p: np.ndarray, q: np.ndarray) -> float:
        start = timer()
        diagonal = _bresenham_pairs(0, 0, p.shape[0], q.shape[0])
        self.times.append(timer() - start)

        start = timer()
        ca = _fast_distance_sparse(p, q, diagonal, self.dist_func)
        self.times.append(timer() - start)

        start = timer()
        ca = _fast_frechet_sparse(ca, diagonal, p, q)
        self.times.append(timer() - start)

        self.ca = ca
        return ca[rc(p.shape[0] - 1, q.shape[0] - 1)]

    def distance(self, p: np.ndarray, q: np.ndarray) -> float:
        ca = _fdfd_sparse(p, q, self.dist_func)
        self.ca = ca
        shape0 = p.shape[0] - 1
        shapeQ = q.shape[0] - 1
        _rc = rc(shape0, shapeQ)
        return ca[_rc]


class FastDiscreteFrechetMatrix(object):
    def __init__(self, dist_func):
        """
        Parameters
        ----------
        dist_func:
        """
        self.times = []
        self.dist_func = dist_func
        self.ca = np.zeros((1, 1))
        # JIT the numba code
        self.distance(
            np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([[0.0, 0.0], [1.0, 1.0]])
        )

    def timed_distance(self, p: np.ndarray, q: np.ndarray) -> float:
        start = timer()
        diagonal = _bresenham_pairs(0, 0, p.shape[0], q.shape[0])
        self.times.append(timer() - start)

        start = timer()
        ca = _fast_distance_matrix(p, q, diagonal, self.dist_func)
        self.times.append(timer() - start)

        start = timer()
        ca = _fast_frechet_matrix(ca, diagonal, p, q)
        self.times.append(timer() - start)

        self.ca = ca
        return ca[p.shape[0] - 1, q.shape[0] - 1]

    def distance(self, p: np.ndarray, q: np.ndarray) -> float:
        ca = _fdfd_matrix(p, q, self.dist_func)
        self.ca = ca
        return ca[p.shape[0] - 1, q.shape[0] - 1]


@jit(nopython=True, fastmath=True)
def euclidean(p: np.ndarray, q: np.ndarray) -> float:
    d = p - q
    return math.sqrt(np.dot(d, d))


@jit(nopython=True, fastmath=True)
def haversine(p: np.ndarray, q: np.ndarray) -> float:
    """
    Vectorized haversine distance calculation
    :p: Initial location in radians
    :q: Final location in radians
    :return: Distance
    """
    d = q - p
    a = (
        math.sin(d[0] / 2.0) ** 2
        + math.cos(p[0]) * math.cos(q[0]) * math.sin(d[1] / 2.0) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return c


@jit(nopython=True, fastmath=True)
def earth_haversine(p: np.ndarray, q: np.ndarray) -> float:
    """
    Vectorized haversine distance calculation
    :p: Initial location in degrees [lat, lon]
    :q: Final location in degrees [lat, lon]
    :return: Distances in meters
    """
    earth_radius = 6378137.0
    return haversine(np.radians(p), np.radians(q)) * earth_radius


def print_sparse_matrix(d: Dict):
    for key, value in d.items():
        col = key & ((1 << 32) - 1)
        row = key >> 32
        print("({0},{1}): {2}".format(row, col, value))
