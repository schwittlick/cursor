import inspect
from typing import List, Tuple, Callable, Optional, Any

import numba as nb
import numpy as np
import pynput
from shapely import LineString
from shapely.affinity import affine_transform

from cursor.position import Position


@nb.njit(fastmath=True, parallel=True)
def calc_distance(vec_1: np.ndarray, vec_2: np.ndarray) -> np.ndarray:
    res = np.empty((vec_1.shape[0], vec_2.shape[0]), dtype=np.float64)
    for i in nb.prange(vec_1.shape[0]):
        for j in range(vec_2.shape[0]):
            res[i, j] = np.sqrt((vec_1[i, 0] - vec_2[j, 0])
                                ** 2 + (vec_1[i, 1] - vec_2[j, 1])
                                ** 2 + (vec_1[i, 2] - vec_2[j, 2]) ** 2)

    return res


def mix(begin: float, end: float, perc: float) -> float:
    return ((end - begin) * perc) + begin


def convert_pynput_btn_to_key(btn: pynput.keyboard.Key) -> Optional[str]:
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

    if btn == pynput.keyboard.Key.tab:
        return "TAB"

    return None


def generate_perlin_noise_2d(shape: Tuple[int, int], res: Tuple[int, int]) -> np.ndarray:
    def f(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0: res[0]: delta[0], 0: res[1]: delta[1]].transpose(1, 2, 0) % 1
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


def map(value: float, in_min: float, in_max: float, out_min: float, out_max: float, clamp: bool = True) -> float:
    out = (value - in_min) / (in_max - in_min) * (out_max - out_min) + out_min

    if clamp:
        if out_max < out_min:
            if out < out_max:
                out = out_max
            elif out > out_min:
                out = out_min
    else:
        if out > out_max:
            out = out_max
        elif out < out_min:
            out = out_min
    return out


def clamp(n: float, smallest: float, largest: float) -> float:
    return max(smallest, min(n, largest))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linear Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (v - a) / (b - a)


def remap(i_min: float, i_max: float, o_min: float, o_max: float, v: float) -> float:
    """Remap values from one linear scale to another, a combination of lerp and inv_lerp.
    i_min and i_max are the scale on which the original value resides,
    o_min and o_max are the scale to which it should be mapped.
    Examples
    --------
        45 == remap(0, 100, 40, 50, 50)
        6.2 == remap(1, 5, 3, 7, 4.2)
    """
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, v))


def current_source(frame: inspect.FrameInfo) -> str:
    return inspect.getsource(inspect.getmodule(frame))


def transformFn(stl: Tuple[float, float],
                sbr: Tuple[float, float],
                dtl: Tuple[float, float],
                dbr: Tuple[float, float]) -> Callable[[Position], Position]:
    """
    ty lars wander
    https://larswander.com/writing/centering-and-scaling/
    """
    stlx, stly = stl
    sbrx, sbry = sbr
    dtlx, dtly = dtl
    dbrx, dbry = dbr

    sdx, sdy = sbrx - stlx, sbry - stly
    ddx, ddy = dbrx - dtlx, dbry - dtly

    ry, rx = ddx / sdx, ddy / sdy
    a = min(rx, ry)

    ox, oy = (ddx - sdx * a) * 0.5 + dtlx, (ddy - sdy * a) * 0.5 + dtly
    bx, by = -stlx * a + ox, -stly * a + oy

    def calc(inp: Position):
        x, y = inp.x, inp.y
        return Position(x * a + bx, y * a + by, 0, inp.properties)

    return calc


def apply_matrix(pa: List[Tuple[float, float]], _ma: Any) -> List[Tuple[float, float]]:
    l = LineString(pa)
    xx, yy, = affine_transform(l, _ma).coords.xy
    return zip(yy, xx)


def line_intersection(ray_origin: np.ndarray,
                      ray_direction: np.ndarray,
                      segment_start: np.ndarray,
                      segment_end: np.ndarray) -> Optional[List[float]]:
    # Calculate differences
    d_se = segment_end - segment_start
    d_ro_s_s = ray_origin - segment_start
    perp_product = np.cross(d_se, ray_direction)

    t = np.cross(d_ro_s_s, ray_direction) / perp_product

    # Check if intersection is within segment bounds
    if 0 <= t <= 1:
        # Calculate intersection point
        intersection = segment_start + t * d_se
        return intersection.tolist()

    # ray and line are parallel
    return None


def split_list_into_chunks(lst: List[Any], n: int) -> List[List[Any]]:
    """Split a list into n chunks of approximately equal size."""
    # Calculate the size of each chunk
    chunk_size = len(lst) // n
    # If the list can't be divided exactly into n chunks,
    # calculate the number of larger chunks that will have one extra element
    larger_chunks = len(lst) - n * chunk_size

    chunks = []
    start = 0
    for i in range(n):
        # The first 'larger_chunks' will have 'chunk_size + 1' elements
        if i < larger_chunks:
            end = start + chunk_size + 1
        else:
            end = start + chunk_size
        # Append the chunk to the list of chunks
        chunks.append(lst[start:end])
        # Update the start for the next chunk
        start = end

    return chunks


def split_list_into_chunks_of_size(lst: List[Any], chunksize: int) -> List[List[Any]]:
    """ Splits list into chunks, where each chunk has certain size. Last chunk will contain remaining """
    for i in range(0, len(lst), chunksize):
        yield lst[i:i + chunksize]
