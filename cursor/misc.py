from cursor import data
from cursor import path
from cursor.renderer import SvgRenderer
from cursor.renderer import JpegRenderer

import time
import numpy as np
import inspect


class Timer:
    def __init__(self):
        self._time = None

    def start(self):
        self._time = time.perf_counter()

    def elapsed(self):
        return time.perf_counter() - self._time

    def print_elapsed(self):
        print(self.elapsed())


def img_to_path(img, lines: int = 660):
    """
    This works only for A3 on HP7579a
    Mit dem neuen zentrierungs-Mechanismus haben wir 33cm in der Höhe
    Mit Stiftstärke von ~0.5mm -> 660 linien
    """
    pc = path.PathCollection()

    rows, cols = img.shape
    for x in range(rows):
        pa = path.Path()
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
                pa = path.Path()
                pass
    return pc


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


def save_wrapper(pc, projname, fname):
    jpeg_folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = JpegRenderer(jpeg_folder)

    jpeg_renderer.render(pc, scale=1.0)
    jpeg_renderer.save(fname)

    svg_folder = data.DataDirHandler().svg(projname)
    svg_renderer = SvgRenderer(svg_folder)

    svg_renderer.render(pc)
    svg_renderer.save(fname)


def save_wrapper_jpeg(pc, projname, fname, scale=4.0, thickness=3):
    folder = data.DataDirHandler().jpg(projname)
    jpeg_renderer = JpegRenderer(folder)

    jpeg_renderer.render(pc, scale=scale, thickness=thickness)
    jpeg_renderer.save(fname)


def current_source(frame):
    return inspect.getsource(inspect.getmodule(frame))
