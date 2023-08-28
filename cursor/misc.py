import inspect

import cv2
import numpy as np
import pynput
import logging
from datetime import datetime

from shapely import LineString
from shapely.affinity import affine_transform

from cursor.position import Position

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


def mix(begin: float, end: float, perc: float):
    return ((end - begin) * perc) + begin


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


def map(value, inputMin, inputMax, outputMin, outputMax, clamp=True):
    outVal = (value - inputMin) / (inputMax - inputMin) * (outputMax - outputMin) + outputMin

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


class ditherModule(object):
    def dither(self, img, method="floyd-steinberg", resize=False):
        if resize:
            img = cv2.resize(
                img,
                (np.int(0.5 * (np.shape(img)[1])), np.int(0.5 * (np.shape(img)[0]))),
            )
        if method == "simple2D":
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + (0.5 * err)
                    out[i + 1][j] = out[i + 1][j] + (0.5 * err)

            return out[1: rows - 1, 1: cols - 1]

        elif method == "floyd-steinberg":
            img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(1, rows - 1):
                for j in range(1, cols - 1):
                    # threshold step
                    if out[i][j] > 0.9:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + ((7 / 16) * err)
                    out[i + 1][j - 1] = out[i + 1][j - 1] + ((3 / 16) * err)
                    out[i + 1][j] = out[i + 1][j] + ((5 / 16) * err)
                    out[i + 1][j + 1] = out[i + 1][j + 1] + ((1 / 16) * err)

            return out[1: rows - 1, 1: cols - 1]

        elif method == "jarvis-judice-ninke":
            img = cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_REPLICATE)
            rows, cols = np.shape(img)
            out = cv2.normalize(img.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)
            for i in range(2, rows - 2):
                for j in range(2, cols - 2):
                    # threshold step
                    if out[i][j] > 0.5:
                        err = out[i][j] - 1
                        out[i][j] = 1
                    else:
                        err = out[i][j]
                        out[i][j] = 0

                    # error diffusion step
                    out[i][j + 1] = out[i][j + 1] + ((7 / 48) * err)
                    out[i][j + 2] = out[i][j + 2] + ((5 / 48) * err)

                    out[i + 1][j - 2] = out[i + 1][j - 2] + ((3 / 48) * err)
                    out[i + 1][j - 1] = out[i + 1][j - 1] + ((5 / 48) * err)
                    out[i + 1][j] = out[i + 1][j] + ((7 / 48) * err)
                    out[i + 1][j + 1] = out[i + 1][j + 1] + ((5 / 48) * err)
                    out[i + 1][j + 2] = out[i + 1][j + 2] + ((3 / 48) * err)

                    out[i + 2][j - 2] = out[i + 2][j - 2] + ((1 / 48) * err)
                    out[i + 2][j - 1] = out[i + 2][j - 1] + ((3 / 48) * err)
                    out[i + 2][j] = out[i + 2][j] + ((5 / 48) * err)
                    out[i + 2][j + 1] = out[i + 2][j + 1] + ((3 / 48) * err)
                    out[i + 2][j + 2] = out[i + 2][j + 2] + ((1 / 48) * err)

            return out[2: rows - 2, 2: cols - 2]

        else:
            raise TypeError(
                'specified method does not exist. available methods = "simple2D", \
                "floyd-steinberg(default)", "jarvis-judice-ninke"'
            )


def current_source(frame):
    return inspect.getsource(inspect.getmodule(frame))


def timestamp(format: str = "%Y%m%d_%H%M%S") -> str:
    now = datetime.now()
    return now.strftime(format)


def transformFn(stl, sbr, dtl, dbr):
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


def apply_matrix(pa: list[tuple], _ma) -> list[tuple]:
    l = LineString(pa)
    xx, yy, = affine_transform(l, _ma).coords.xy
    return zip(yy, xx)
