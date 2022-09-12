import time
import numpy as np
import inspect
import pynput


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
