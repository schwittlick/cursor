import time
import numpy as np
import inspect
import pynput
import wasabi

log = wasabi.Printer()


def mix(begin: float, end: float, perc: float):
    return ((end - begin) * perc) + begin


class Timer:
    def __init__(self):
        self.start()

    def start(self):
        self._time = time.perf_counter()

    def elapsed(self):
        t1 = time.perf_counter()
        return t1 - self._time

    def print_elapsed(self, msg):
        log.info(f"{msg}: {round(self.elapsed() * 1000)}ms")


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


def parse_hpgl(gl_file):
    """Convert HP Graphics Language (HPGL) to list of paths"""

    """
    Copyright (c) 2015 Alex Forencich
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    """

    border = 10

    pen_down = False
    cur_pen = 1
    cur_x = 0
    cur_y = 0
    cto_x = 0 # text offset
    cto_y = 0

    std_font = 48
    alt_font = 48
    cur_font = 48

    char_rel_width = 0.0075
    char_rel_height = 0.0075

    char_abs_width = 0
    char_abs_height = 0

    pen_width = 1
    stroke_weight = 0

    label_term = chr(3)
    label_term_print = False

    paths = []
    labels = []

    if type(gl_file) == str:
        glf = open(gl_file, 'rb')
    else:
        glf = gl_file

    while True:
        c = glf.read(1)
        while c == ';' or c == ' ' or c == '\r' or c == '\n':
            c = glf.read(1)
        cmd = c + glf.read(1)
        cmd = cmd.upper()

        if len(cmd) < 2:
            break

        if cmd == 'PU':
            # pen up
            pen_down = False
        elif cmd == 'PD':
            # pen down
            pen_down = True
        elif cmd == 'SP':
            # select pen
            c = glf.read(1)
            if c == ';':
                continue
            cur_pen = int(c)
        elif cmd == 'LT':
            pass
        elif cmd == 'SA':
            # select alternate
            cur_font = alt_font
        elif cmd == 'SS':
            # select standard
            cur_font = std_font
        elif cmd == 'SR':
            # specify relative character sizes
            s = ''
            c = glf.read(1)
            while c != ',':
                s += c
                c = glf.read(1)
            char_rel_width = float(s)/100.0
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            char_rel_height = float(s)/100.0
        elif cmd == 'SI':
            # specify absolute character sizes
            s = ''
            c = glf.read(1)
            while c != ',':
                s += c
                c = glf.read(1)
            char_abs_width = float(s)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            char_abs_height = float(s)
        elif cmd == 'PA':
            # plot absolute

            c = ''
            pts = [(cur_x, cur_y, cto_x, cto_y)]

            while c != ';':
                s = ''
                c = glf.read(1)
                if c == ';':
                    cur_x = 0
                    cur_y = 0
                    cto_x = 0
                    cto_y = 0
                    pts.append((0,0,0,0))
                    break
                while c == '-' or ord(c) >= 48 and ord(c) <= 57:
                    s += c
                    c = glf.read(1)

                cur_x = int(s)

                s = ''
                c = glf.read(1)
                while c == '-' or ord(c) >= 48 and ord(c) <= 57:
                    s += c
                    c = glf.read(1)

                cur_y = int(s)

                cto_x = 0
                cto_y = 0

                pts.append((cur_x, cur_y, 0, 0))

            if pen_down:
                paths.append((cur_pen, pen_width, pts))
        elif cmd == 'LB':
            # label

            c = glf.read(1)
            x = cur_x
            y = cur_y
            tx = cto_x
            ty = cto_y
            while label_term_print or c != label_term:
                if ord(c) == 8:
                    cto_x -= char_rel_width * 3/2
                elif ord(c) == 10:
                    cto_x = tx
                    cto_y -= char_rel_height * 2
                elif ord(c) < 32:
                    pass
                else:
                    labels.append((cur_x, cur_y, cto_x, cto_y, char_rel_width, char_rel_height, cur_pen, cur_font, c))
                    cto_x += char_rel_width * 3/2
                    if c == label_term:
                        break
                c = glf.read(1)
        elif cmd == 'DI':
            # absolute direction
            s = ''
            c = glf.read(1)
            if c == ';':
                #run = 1
                #rise = 0
                continue
            while c != ',':
                s += c
                c = glf.read(1)
            #run = float(s)
            s = ''
            c = glf.read(1)
            while c != ';':
                s += c
                c = glf.read(1)
            #rise = float(s)
        elif cmd == 'DF':
            # defaults
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cto_x = 0
            cto_y = 0

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.0075

            label_term = chr(3)
            label_term_print = False
        elif cmd == 'IN':
            # init
            pen_down = False
            cur_pen = 1
            cur_x = 0
            cur_y = 0
            cto_x = 0
            cto_y = 0

            std_font = 48
            alt_font = 48
            cur_font = 48

            char_rel_width = 0.0075
            char_rel_height = 0.0075

            label_term = chr(3)
            label_term_print = False
        elif cmd == 'OP':
            # output P1 and P2 - ignored
            pass
        else:
            raise Exception("Unknown HPGL command (%s)" % cmd)

    # determine size
    max_x = 0
    max_y = 0

    # max extent of vector graphics
    for path in paths:
        pen, width, pts = path
        for p in pts:
            max_x = max(p[0], max_x)
            max_y = max(p[1], max_y)

    # max extent of text
    for lb in labels:
        max_x = max(lb[0]/(1-(lb[2]+lb[4])), max_x)
        max_y = max(lb[1]/(1-(lb[3]+lb[5])), max_y)

    max_x = round(max_x+0.5)
    max_y = round(max_y+0.5)

    # add text offsets
    paths2 = []
    for path in paths:
        pen, width, pts = path
        pts2 = []
        for p in pts:
            pts2.append((p[0] + p[2]*max_x, p[1] + p[3]*max_y))
        paths2.append((pen, width, pts2))
    paths = paths2

    # render text
    for lb in labels:
        x, y, tx, ty, cw, ch, pen, font, c = lb
        width = cw*max_x
        height = ch*max_y
        x += tx*max_x
        y += ty*max_y
        if stroke_weight < 9999:
            pw = 0.1 * min(height, 1.5*width) * 1.13**stroke_weight
        else:
            pw = pen_width
        if c in stick_font:
            chr_paths = stick_font[c]
            for pts in chr_paths:
                path = []
                for p in pts:
                    path.append((p[0]/4*width+x, p[1]/8*height+y))
                paths.append((pen, pw, path))

    max_x += border*2
    max_y += border*2

    # flip y axis and shift
    paths2 = []
    for path in paths:
        pen, width, pts = path
        pts2 = []
        for p in pts:
            pts2.append((p[0]+border, max_y-p[1]-border))
        paths2.append((pen, width, pts2))

    return paths2, max_x, max_y


stick_font = {
    '!': [[(0.125, 2.75), (0.125, 8.0)], [(0.0, 0.0), (0.0, 0.5), (0.25, 0.5), (0.25, 0.0), (0.0, 0.0)]],
    '"': [[(1.25, 6.5), (1.25, 9.0)], [(2.75, 6.5), (2.75, 9.0)]],
    '#': [[(0.5, 0.0), (2.0, 8.0)], [(2.0, 0.0), (3.5, 8.0)], [(0.0, 3.0), (4.0, 3.0)], [(0.0, 5.0), (4.0, 5.0)]],
    '$': [[(2.0, -1.0), (2.0, 9.0)], [(0.0, 1.5), (0.25, 0.75), (0.875, 0.25), (3.125, 0.25), (3.75, 0.75), (4.0, 1.5), (4.0, 2.75), (3.75, 3.5), (3.125, 4.0), (0.875, 4.25), (0.25, 4.75), (0.0, 5.5), (0.0, 6.5), (0.25, 7.25), (0.875, 7.75), (3.0, 7.75), (3.625, 7.25), (3.875, 6.5)]],
    '%': [[(0.0, 0.0), (4.0, 8.0)], [(3.5, 0.0), (3.875, 0.25), (4.0, 0.75), (4.0, 2.0), (3.875, 2.5), (3.5, 2.75), (2.75, 2.75), (2.375, 2.5), (2.25, 2.0), (2.25, 0.75), (2.375, 0.25), (2.75, 0.0), (3.5, 0.0)], [(1.25, 5.25), (1.625, 5.5), (1.75, 6.0), (1.75, 7.25), (1.625, 7.75), (1.25, 8.0), (0.5, 8.0), (0.125, 7.75), (0.0, 7.25), (0.0, 6.0), (0.125, 5.5), (0.5, 5.25), (1.25, 5.25)]],
    '&': [[(4.0, 0.0), (0.75, 5.25), (0.5, 6.0), (0.5, 7.0), (0.75, 7.75), (1.375, 8.0), (2.75, 8.0), (3.375, 7.75), (3.625, 7.0), (3.625, 6.25)], [(4.0, 3.25), (4.0, 1.75), (3.75, 0.75), (3.25, 0.25), (2.625, 0.0), (1.375, 0.0), (0.75, 0.25), (0.25, 0.75), (0.0, 1.75), (0.0, 3.0), (0.25, 4.0), (1.0, 4.75)]],
    '\'': [[(1.875, 6.75), (2.125, 7.0), (2.25, 7.25), (2.25, 8.5), (1.875, 8.5), (1.875, 8.0), (2.25, 8.0)]],
    '(': [[(4.0, -1.0), (3.5, 0.0), (3.125, 1.25), (3.0, 2.5), (3.0, 5.5), (3.125, 6.75), (3.5, 8.0), (4.0, 9.0)]],
    ')': [[(0.0, -1.0), (0.5, 0.0), (0.875, 1.25), (1.0, 2.5), (1.0, 5.5), (0.875, 6.75), (0.5, 8.0), (0.0, 9.0)]],
    '*': [[(0.5, 1.0), (3.5, 7.0)], [(3.5, 1.0), (0.5, 7.0)], [(0.0, 4.0), (4.0, 4.0)]],
    '+': [[(0.0, 4.0), (4.0, 4.0)], [(2.0, 7.0), (2.0, 1.0)]],
    ',': [[(0.0, -1.25), (0.25, -1.0), (0.375, -0.75), (0.375, 0.5), (0.0, 0.5), (0.0, 0.0), (0.375, 0.0)]],
    '-': [[(0.0, 4.0), (4.0, 4.0)]],
    '.': [[(2.25, 0.0), (2.25, 0.5), (1.875, 0.5), (1.875, 0.0), (2.25, 0.0)]],
    '/': [[(0.0, -1.0), (4.0, 9.0)]],
    '0': [[(0.0, 3.0), (0.25, 1.75), (0.5, 1.0), (1.0, 0.25), (1.5, 0.0), (2.25, 0.0), (2.75, 0.25), (3.25, 0.975), (3.5, 1.75), (3.75, 3.0), (3.75, 5.0), (3.5, 6.25), (3.25, 7.0), (2.75, 7.75), (2.275, 8.0), (1.5, 8.0), (1.0, 7.75), (0.5, 7.0), (0.25, 6.25), (0.0, 5.0), (0.0, 3.0)]],
    '1': [[(1.0, 0.0), (3.5, 0.0)], [(1.0, 5.0), (2.5, 8.0), (2.5, 0.0)]],
    '2': [[(4.0, 0.0), (0.0, 0.0), (0.125, 1.75), (0.375, 2.5), (0.75, 3.0), (1.375, 3.25), (3.25, 3.75), (3.75, 4.25), (4.0, 5.0), (4.0, 6.5), (3.75, 7.25), (3.25, 7.75), (2.65, 8.0), (1.5, 8.0), (0.875, 7.75), (0.375, 7.25), (0.125, 6.5)]],
    '3': [[(0.125, 7.0), (0.625, 7.75), (1.125, 8.0), (2.775, 8.0), (3.375, 7.75), (3.75, 7.25), (3.875, 6.5), (3.875, 5.75), (3.75, 5.0), (3.3375, 4.5), (2.75, 4.25), (1.375, 4.25)], [(2.75, 4.25), (3.5, 4.0), (3.875, 3.5), (4.0, 2.75), (4.0, 1.5), (3.875, 0.75), (3.5, 0.25), (2.75, 0.0), (1.25, 0.0), (0.5, 0.25), (0.0, 1.0)]],
    '4': [[(3.5, 0.0), (3.5, 8.0), (0.0, 2.0), (4.0, 2.0)]],
    '5': [[(3.9, 8.0), (0.0, 8.0), (0.0, 4.0), (0.5, 5.0), (1.125, 5.25), (2.875, 5.25), (3.5, 5.0), (3.875, 4.5), (4.0, 3.5), (4.0, 1.75), (3.875, 0.75), (3.5, 0.25), (2.9, 0.0), (1.1, 0.0), (0.5, 0.25), (0.125, 0.75), (0.0, 1.25)]],
    '6': [[(3.875, 7.25), (3.5, 7.75), (2.9, 8.0), (1.25, 8.0), (0.625, 7.75), (0.25, 7.25), (0.0, 6.0), (0.0, 3.25)], [(0.0, 3.25), (0.0, 2.0), (0.25, 0.75), (0.625, 0.25), (1.25, 0.0), (2.75, 0.0), (3.375, 0.25), (3.75, 0.75), (4.0, 1.5), (4.0, 3.25), (3.75, 4.0), (3.375, 4.5), (2.75, 4.75), (1.25, 4.75), (0.625, 4.5), (0.25, 4.0), (0.0, 3.25)]],
    '7': [[(0.0, 8.0), (4.0, 8.0), (1.0, 0.0)]],
    '8': [[(1.25, 4.25), (0.625, 4.5), (0.25, 5.0), (0.125, 5.75), (0.125, 6.5), (0.25, 7.25), (0.625, 7.75), (1.25, 8.0), (2.775, 8.0), (3.375, 7.75), (3.75, 7.25), (3.875, 6.5), (3.875, 5.75), (3.75, 5.0), (3.375, 4.5), (2.75, 4.25), (1.25, 4.25)], [(1.25, 4.25), (0.5, 4.0), (0.125, 3.5), (0.0, 2.8), (0.0, 1.5), (0.125, 0.75), (0.5, 0.25), (1.25, 0.0), (2.75, 0.0), (3.5, 0.25), (3.875, 0.75), (4.0, 1.5), (4.0, 2.8), (3.875, 3.5), (3.5, 4.0), (2.75, 4.25)]],
    '9': [[(4.0, 4.75), (4.0, 6.0), (3.75, 7.25), (3.375, 7.75), (2.75, 8.0), (1.25, 8.0), (0.625, 7.75), (0.25, 7.25), (0.0, 6.5), (0.0, 4.75), (0.25, 4.0), (0.625, 3.5), (1.25, 3.25), (2.75, 3.25), (3.375, 3.5), (3.75, 4.0), (4.0, 4.75)], [(4.0, 4.75), (4.0, 2.0), (3.75, 0.75), (3.375, 0.25), (2.775, 0.0), (1.1, 0.0), (0.5, 0.25), (0.125, 0.75)]],
    ':': [[(0.0, 6.0), (0.375, 6.0), (0.375, 5.5), (0.0, 5.5), (0.0, 6.0)], [(0.0, 0.5), (0.375, 0.5), (0.375, 0.0), (0.0, 0.0), (0.0, 0.5)]],
    ';': [[(0.0, 6.0), (0.375, 6.0), (0.375, 5.5), (0.0, 5.5), (0.0, 6.0)], [(0.0, -1.25), (0.25, -1.0), (0.375, -0.75), (0.375, 0.5), (0.0, 0.5), (0.0, 0.0), (0.375, 0.0)]],
    '<': [[(4.0, 7.0), (0.0, 4.0), (4.0, 1.0)]],
    '=': [[(0.0, 5.0), (4.0, 5.0)], [(0.0, 3.0), (4.0, 3.0)]],
    '>': [[(0.0, 7.0), (4.0, 4.0), (0.0, 1.0)]],
    '?': [[(1.0, 0.5), (1.375, 0.5), (1.375, 0.0), (1.0, 0.0), (1.0, 0.5)], [(1.125, 2.5), (1.25, 3.25), (1.5, 3.75), (2.5, 4.5), (2.75, 5.25), (2.75, 6.75), (2.5, 7.5), (1.875, 8.0), (0.875, 8.0), (0.25, 7.5), (0.0, 6.75)]],
    '@': [[(4.0, 4.75), (3.625, 5.5), (3.125, 5.75), (2.0, 5.75), (1.5, 5.5), (1.125, 4.75), (1.125, 3.25), (1.5, 2.5), (2.0, 2.25), (3.125, 2.25), (3.625, 2.5), (4.0, 3.25), (4.0, 4.75)], [(4.0, 4.75), (4.0, 6.0), (3.875, 7.0), (3.5, 7.75), (2.75, 8.0), (1.25, 8.0), (0.5, 7.75), (0.125, 7.0), (0.0, 6.0), (0.0, 1.95), (0.125, 1.0), (0.5, 0.25), (1.25, 0.0), (3.5, 0.0)]],
    'A': [[(0.0, 0.0), (2.0, 8.0), (4.0, 0.0)], [(0.5, 2.0), (3.5, 2.0)]],
    'B': [[(0.0, 4.25), (0.0, 8.0), (2.9, 8.0), (3.25, 7.75), (3.625, 7.25), (3.75, 6.5), (3.75, 5.75), (3.625, 5.0), (3.25, 4.5), (2.875, 4.25), (0.0, 4.25)], [(2.875, 4.25), (3.375, 4.0), (3.75, 3.5), (4.0, 2.75), (4.0, 1.5), (3.75, 0.75), (3.375, 0.25), (2.9, 0.0), (0.0, 0.0), (0.0, 4.25)]],
    'C': [[(3.875, 6.25), (3.75, 7.25), (3.375, 7.75), (2.65, 8.0), (1.475, 8.0), (0.75, 7.75), (0.375, 7.275), (0.125, 6.5), (0.0, 5.1), (0.0, 2.9), (0.125, 1.5), (0.35, 0.75), (0.75, 0.25), (1.5, 0.0), (2.65, 0.0), (3.375, 0.25), (3.75, 0.75), (3.875, 1.75)]],
    'D': [[(2.4, 8.0), (3.25, 7.75), (3.625, 7.25), (3.875, 6.5), (4.0, 5.0), (4.0, 2.9), (3.875, 1.5), (3.625, 0.75), (3.25, 0.25), (2.5, 0.0), (0.0, 0.0), (0.0, 8.0), (2.4, 8.0)]],
    'E': [[(4.0, 8.0), (0.0, 8.0), (0.0, 0.0), (4.0, 0.0)], [(0.0, 4.25), (3.25, 4.25)]],
    'F': [[(4.0, 8.0), (0.0, 8.0), (0.0, 0.0)], [(0.0, 4.25), (3.0, 4.25)]],
    'G': [[(3.875, 6.5), (3.625, 7.25), (3.25, 7.75), (2.5, 8.0), (1.5, 8.0), (0.75, 7.75), (0.375, 7.25), (0.125, 6.5), (0.0, 5.1), (0.0, 3.0), (0.125, 1.5), (0.375, 0.75), (0.75, 0.25), (1.5, 0.0), (2.5, 0.0), (3.25, 0.25), (3.625, 0.75), (3.875, 1.5), (4.0, 2.9), (4.0, 3.75)], [(4.0, 3.75), (2.0, 3.75)]],
    'H': [[(0.0, 8.0), (0.0, 0.0)], [(4.0, 8.0), (4.0, 0.0)], [(0.0, 4.25), (4.0, 4.25)]],
    'I': [[(0.5, 8.0), (3.5, 8.0)], [(2.0, 8.0), (2.0, 0.0)], [(0.5, 0.0), (3.5, 0.0)]],
    'J': [[(4.0, 8.0), (4.0, 3.0), (3.875, 1.5), (3.625, 0.75), (3.25, 0.25), (2.5, 0.0), (1.5, 0.0), (0.75, 0.25), (0.375, 0.75), (0.125, 1.5), (0.0, 3.0)]],
    'K': [[(0.0, 8.0), (0.0, 0.0)], [(0.0, 4.25), (1.25, 4.25)], [(3.75, 8.0), (1.25, 4.25), (4.0, 0.0)]],
    'L': [[(0.0, 8.0), (0.0, 0.0), (4.0, 0.0)]],
    'M': [[(0.0, 0.0), (0.0, 8.0), (2.0, 2.0), (4.0, 8.0), (4.0, 0.0)]],
    'N': [[(0.0, 0.0), (0.0, 8.0), (4.0, 0.0), (4.0, 8.0)]],
    'O': [[(2.5, 0.0), (3.25, 0.25), (3.625, 0.75), (3.875, 1.5), (4.0, 2.9), (4.0, 5.0), (3.875, 6.5), (3.625, 7.25), (3.25, 7.75), (2.5, 8.0), (1.5, 8.0), (0.75, 7.75), (0.375, 7.25), (0.125, 6.5), (0.0, 5.0), (0.0, 2.9), (0.125, 1.5), (0.375, 0.75), (0.75, 0.25), (1.5, 0.0), (2.5, 0.0)]],
    'P': [[(0.0, 0.0), (0.0, 8.0), (3.0, 8.0), (3.5, 7.725), (3.875, 7.25), (4.0, 6.5), (4.0, 5.0), (3.875, 4.25), (3.5, 3.75), (3.0, 3.5), (0.0, 3.5)]],
    'Q': [[(2.5, 0.0), (3.25, 0.25), (3.625, 0.75), (3.875, 1.5), (4.0, 3.0), (4.0, 5.0), (3.875, 6.5), (3.625, 7.25), (3.25, 7.75), (2.5, 8.0), (1.5, 8.0), (0.75, 7.75), (0.375, 7.25), (0.125, 6.5), (0.0, 5.0), (0.0, 3.0), (0.125, 1.5), (0.35, 0.75), (0.75, 0.25), (1.5, 0.0), (2.5, 0.0)], [(2.5, 3.25), (4.0, 0.0)]],
    'R': [[(0.0, 0.0), (0.0, 8.0), (3.0, 8.0), (3.5, 7.75), (3.875, 7.25), (4.0, 6.5), (4.0, 5.0), (3.875, 4.25), (3.5, 3.725), (3.0, 3.5), (3.5, 3.25), (3.875, 2.75), (4.0, 2.0), (4.0, 0.0)], [(0.0, 3.5), (3.0, 3.5)]],
    'S': [[(3.875, 6.5), (3.75, 7.25), (3.375, 7.75), (2.75, 8.0), (1.1, 8.0), (0.5, 7.75), (0.125, 7.25), (0.0, 6.5), (0.0, 5.7), (0.125, 5.0), (0.5, 4.5), (1.125, 4.25)], [(1.125, 4.25), (2.9, 4.0), (3.5, 3.75), (3.875, 3.25), (4.0, 2.5), (4.0, 1.5), (3.875, 0.75), (3.5, 0.25), (2.9, 0.0), (1.1, 0.0), (0.5, 0.25), (0.125, 0.75), (0.0, 1.5)]],
    'T': [[(0.0, 8.0), (4.0, 8.0)], [(2.0, 8.0), (2.0, 0.0)]],
    'U': [[(0.0, 8.0), (0.0, 3.0), (0.125, 1.5), (0.375, 0.75), (0.75, 0.25), (1.5, 0.0), (2.5, 0.0), (3.25, 0.25), (3.625, 0.75), (3.875, 1.5), (4.0, 3.0), (4.0, 8.0)]],
    'V': [[(0.0, 8.0), (2.0, 0.0), (4.0, 8.0)]],
    'W': [[(0.0, 8.0), (0.5, 0.0), (2.0, 6.0), (3.5, 0.0), (4.0, 8.0)]],
    'X': [[(0.125, 8.0), (4.0, 0.0)], [(0.0, 0.0), (3.875, 8.0)]],
    'Y': [[(0.0, 8.0), (2.0, 3.5), (4.0, 8.0)], [(2.0, 3.5), (2.0, 0.0)]],
    'Z': [[(0.125, 8.0), (3.875, 8.0), (0.0, 0.0), (4.0, 0.0)]],
    '[': [[(4.0, 9.0), (2.75, 9.0), (2.75, -1.0), (4.0, -1.0)]],
    '\\': [[(0.0, 9.0), (4.0, -1.0)]],
    ']': [[(0.0, 9.0), (1.25, 9.0), (1.25, -1.0), (0.0, -1.0)]],
    '^': [[(0.5, 7.5), (1.75, 9.0), (3.0, 7.5)]],
    '_': [[(0.0, -1.5), (6.0, -1.5)]],
    '`': [[(1.0, 9.5), (2.5, 7.5)]],
    'a': [[(1.0, 3.5), (0.5, 3.25), (0.125, 2.75), (0.0, 2.0), (0.0, 1.5), (0.125, 0.75), (0.5, 0.25), (1.125, 0.0), (2.5, 0.0), (3.125, 0.25), (3.375, 0.75), (3.5, 1.5), (3.5, 2.0), (3.375, 2.75), (3.0, 3.25), (2.5, 3.5), (1.0, 3.5)], [(3.5, 0.0), (3.5, 4.0), (3.375, 5.0), (3.0, 5.75), (2.275, 6.0), (1.225, 6.0), (0.5, 5.75), (0.25, 5.5)]],
    'b': [[(0.0, 8.0), (0.0, 0.0)], [(0.0, 4.0), (0.125, 5.0), (0.5, 5.75), (1.1, 6.0), (2.4, 6.0), (3.0, 5.75), (3.375, 5.0), (3.5, 4.0), (3.5, 1.975), (3.375, 1.0), (3.0, 0.25), (2.4, 0.0), (1.1, 0.0), (0.5, 0.25), (0.125, 1.0), (0.0, 1.975), (0.0, 4.0)]],
    'c': [[(3.375, 5.0), (3.0, 5.75), (2.375, 6.0), (1.125, 6.0), (0.5, 5.75), (0.125, 5.0), (0.0, 4.0), (0.0, 2.0), (0.125, 1.0), (0.5, 0.25), (1.1, 0.0), (2.375, 0.0), (3.0, 0.25), (3.375, 1.0)]],
    'd': [[(3.5, 0.0), (3.5, 8.0)], [(3.5, 4.0), (3.375, 5.0), (3.0, 5.75), (2.375, 6.0), (1.125, 6.0), (0.5, 5.75), (0.125, 5.0), (0.0, 4.0), (0.0, 2.0), (0.125, 1.0), (0.5, 0.25), (1.1, 0.0), (2.4, 0.0), (3.0, 0.25), (3.375, 1.0), (3.5, 2.0), (3.5, 4.0)]],
    'e': [[(0.0, 3.25), (3.5, 3.25), (3.5, 4.0), (3.375, 5.0), (3.0, 5.75), (2.375, 6.0), (1.125, 6.0), (0.5, 5.75), (0.125, 5.0), (0.0, 4.0), (0.0, 2.0), (0.125, 1.0), (0.5, 0.25), (1.1, 0.0), (2.4, 0.0), (3.0, 0.25), (3.375, 1.0)]],
    'f': [[(3.125, 8.0), (2.5, 8.0), (2.0, 7.75), (1.625, 7.25), (1.5, 6.5), (1.5, 0.0)], [(0.5, 5.25), (3.125, 5.25)]],
    'g': [[(3.5, 6.0), (3.5, 0.0), (3.375, -1.0), (3.0, -1.75), (2.375, -2.0), (1.0, -2.0), (0.25, -1.5)], [(3.5, 4.0), (3.375, 5.0), (3.0, 5.75), (2.375, 6.0), (1.125, 6.0), (0.5, 5.75), (0.125, 5.0), (0.0, 4.0), (0.0, 2.5), (0.125, 1.5), (0.5, 0.75), (1.125, 0.5), (2.375, 0.5), (3.0, 0.75), (3.375, 1.5), (3.5, 2.5), (3.5, 4.0)]],
    'h': [[(0.0, 8.0), (0.0, 0.0)], [(0.0, 4.0), (0.25, 5.0), (0.625, 5.75), (1.25, 6.0), (2.375, 6.0), (3.0, 5.75), (3.375, 5.0), (3.5, 4.0), (3.5, 0.0)]],
    'i': [[(1.75, 8.0), (1.75, 7.5)], [(0.75, 5.5), (2.25, 5.5), (2.25, 0.0)], [(0.75, 0.0), (3.25, 0.0)]],
    'j': [[(1.75, 8.0), (1.75, 7.5)], [(0.75, 5.5), (2.25, 5.5), (2.25, -0.5), (2.125, -1.25), (1.75, -1.75), (1.25, -2.0), (0.75, -2.0)]],
    'k': [[(0.0, 8.0), (0.0, 0.0)], [(0.0, 3.25), (0.75, 3.25)], [(3.25, 6.0), (0.75, 3.25), (3.5, 0.0)]],
    'l': [[(0.75, 8.0), (2.25, 8.0), (2.25, 0.0)], [(0.75, 0.0), (3.25, 0.0)]],
    'm': [[(0.0, 6.0), (0.0, 0.0)], [(0.0, 4.5), (0.125, 5.25), (0.375, 5.75), (0.75, 6.0), (1.25, 6.0), (1.625, 5.75), (1.875, 5.25), (2.0, 4.5), (2.125, 5.25), (2.375, 5.75), (2.75, 6.0), (3.25, 6.0), (3.625, 5.75), (3.875, 5.25), (4.0, 4.5), (4.0, 0.0)], [(2.0, 4.5), (2.0, 0.0)]],
    'n': [[(0.0, 6.0), (0.0, 0.0)], [(0.0, 4.0), (0.25, 5.0), (0.625, 5.75), (1.25, 6.0), (2.375, 6.0), (3.0, 5.75), (3.375, 5.0), (3.5, 4.0), (3.5, 0.0)]],
    'o': [[(1.125, 6.0), (0.5, 5.75), (0.125, 5.0), (0.0, 4.0), (0.0, 2.0), (0.125, 1.0), (0.5, 0.25), (1.125, 0.0), (2.375, 0.0), (3.0, 0.25), (3.375, 1.0), (3.5, 2.0), (3.5, 4.0), (3.375, 5.0), (3.0, 5.75), (2.375, 6.0), (1.125, 6.0)]],
    'p': [[(0.0, 6.0), (0.0, -2.0)], [(0.0, 4.0), (0.125, 5.0), (0.5, 5.75), (1.1, 6.0), (2.4, 6.0), (3.0, 5.75), (3.375, 5.0), (3.5, 4.0), (3.5, 2.0), (3.375, 1.0), (3.0, 0.25), (2.375, 0.0), (1.125, 0.0), (0.5, 0.25), (0.125, 1.0), (0.0, 2.0), (0.0, 4.0)]],
    'q': [[(3.5, 6.0), (3.5, -2.0)], [(3.5, 4.0), (3.375, 5.0), (3.0, 5.75), (2.375, 6.0), (1.125, 6.0), (0.5, 5.75), (0.125, 5.0), (0.0, 4.0), (0.0, 2.0), (0.125, 1.0), (0.5, 0.25), (1.125, 0.0), (2.375, 0.0), (3.0, 0.25), (3.375, 1.0), (3.5, 2.0), (3.5, 4.0)]],
    'r': [[(0.0, 6.0), (0.0, 0.0)], [(0.0, 4.0), (0.25, 5.0), (0.625, 5.75), (1.225, 6.0), (2.375, 6.0), (3.0, 5.75), (3.375, 5.0), (3.5, 4.0)]],
    's': [[(3.375, 5.0), (3.25, 5.5), (3.0, 5.75), (2.4, 6.0), (1.0, 6.0), (0.375, 5.75), (0.125, 5.5), (0.0, 5.0), (0.0, 4.25), (0.125, 3.75), (0.375, 3.5), (1.0, 3.25)], [(1.0, 3.25), (2.5, 3.25), (3.125, 3.0), (3.375, 2.5), (3.5, 2.0), (3.5, 1.25), (3.375, 0.75), (3.125, 0.25), (2.5, 0.0), (1.0, 0.0), (0.375, 0.25), (0.125, 0.75), (0.0, 1.25)]],
    't': [[(0.0, 5.5), (3.0, 5.5)], [(1.0, 8.0), (1.0, 1.5), (1.125, 0.75), (1.5, 0.25), (2.0, 0.0), (3.0, 0.0), (3.5, 0.5)]],
    'u': [[(3.5, 0.0), (3.5, 6.0)], [(0.0, 6.0), (0.0, 1.975), (0.125, 1.0), (0.5, 0.25), (1.125, 0.0), (2.275, 0.0), (2.875, 0.25), (3.25, 1.0), (3.5, 2.0)]],
    'v': [[(0.0, 6.0), (1.75, 0.0), (3.5, 6.0)]],
    'w': [[(0.0, 6.0), (0.625, 0.0), (2.0, 4.5), (3.375, 0.0), (4.0, 6.0)]],
    'x': [[(0.125, 6.0), (3.5, 0.0)], [(0.0, 0.0), (3.375, 6.0)]],
    'y': [[(0.0, 6.0), (2.0, 0.0)], [(3.5, 6.0), (2.0, 0.0), (1.625, -1.25), (1.375, -1.75), (1.0, -2.0), (0.625, -2.0)]],
    'z': [[(0.125, 6.0), (3.375, 6.0), (0.0, 0.0), (3.5, 0.0)]],
    '{': [[(4.0, 9.0), (3.625, 9.0), (3.375, 8.75), (3.25, 8.25), (3.25, 5.25), (3.125, 4.75), (2.875, 4.25), (2.5, 4.0), (2.875, 3.75), (3.125, 3.25), (3.25, 2.75), (3.25, -0.25), (3.375, -0.75), (3.625, -1.0), (4.0, -1.0)]],
    '|': [[(0.0, 9.0), (0.0, -1.0)]],
    '}': [[(0.0, 9.0), (0.375, 9.0), (0.625, 8.75), (0.75, 8.25), (0.75, 5.25), (0.875, 4.75), (1.125, 4.25), (1.5, 4.0), (1.125, 3.75), (0.875, 3.25), (0.75, 2.75), (0.75, -0.25), (0.625, -0.75), (0.375, -1.0), (0.0, -1.0)]],
    '~': [[(0.0, 7.5), (0.5, 8.5), (0.875, 8.75), (1.25, 8.75), (1.5, 8.5), (2.0, 7.75), (2.25, 7.5), (2.625, 7.5), (3.0, 7.75), (3.5, 8.75)]],
    'Ñ': [[(0.75, 5.5), (2.25, 5.5), (2.25, 0.0)], [(0.75, 0.0), (3.25, 0.0)], [(0.5, 7.5), (1.75, 9.0), (3.0, 7.5)]],
    'Ò': [[(0.0, 0.0), (4.0, 8.0)], [(0.0, 5.5), (0.25, 7.0), (0.625, 7.75), (1.5, 8.0), (2.5, 8.0), (3.375, 7.75), (3.75, 7.0), (4.0, 5.5), (4.0, 2.5), (3.75, 1.0), (3.375, 0.25), (2.5, 0.0), (1.5, 0.0), (0.625, 0.25), (0.25, 1.0), (0.0, 2.5), (0.0, 5.5)]],
    'Ó': [[(0.0, 0.0), (1.75, 8.0), (4.0, 8.0), (4.0, 8.0)], [(2.175, 8.0), (2.175, 0.0), (4.0, 0.0)], [(0.975, 4.0), (4.0, 4.0)]],
    'Ù': [[(0.75, 5.5), (2.25, 5.5), (2.25, 0.0)], [(0.75, 0.0), (3.25, 0.0)], [(1.25, 9.5), (2.75, 7.5)]],
    'ð': [[(0.0, 8.0), (1.5, 8.0)], [(0.5, 8.0), (0.5, -2.0)], [(0.0, -2.0), (1.5, -2.0)], [(0.5, 5.0), (3.0, 5.0), (3.5, 4.75), (3.875, 4.25), (4.0, 3.5), (4.0, 2.5), (3.875, 1.75), (3.5, 1.25), (3.0, 1.0), (0.5, 1.0)]],
    'ñ': [[(0.0, 8.0), (0.0, -2.0)], [(0.0, 4.0), (0.125, 5.0), (0.5, 5.75), (1.125, 6.0), (2.375, 6.0), (3.0, 5.75), (3.375, 5.0), (3.5, 4.0), (3.5, 2.0), (3.375, 1.0), (3.0, 0.25), (2.375, 0.0), (1.125, 0.0), (0.5, 0.25), (0.125, 1.0), (0.0, 2.0), (0.0, 4.0)]],
    'ò': [[(2.0, 4.25), (2.125, 4.25), (2.125, 4.0), (2.0, 4.0), (2.0, 4.25)]],
    'ó': [[(0.0, -2.0), (0.5, 6.0)], [(0.25, 2.0), (0.375, 1.25), (0.625, 0.5), (1.125, 0.0), (2.0, 0.0), (2.375, 0.25), (2.75, 1.0), (3.0, 2.0), (3.25, 6.0)], [(3.0, 2.0), (3.0, 1.0), (3.125, 0.25), (3.375, 0.0), (3.75, 0.25), (4.0, 1.25)]],
    'ô': [[(2.125, 8.0), (2.125, 0.0)], [(3.25, 8.0), (3.25, 0.0)], [(3.75, 8.0), (3.25, 8.0), (2.125, 8.0), (1.25, 8.0), (0.75, 7.75), (0.375, 7.25), (0.25, 6.5), (0.25, 6.0), (0.375, 5.25), (0.75, 4.75), (1.25, 4.5), (2.125, 4.5), (2.125, 4.5)]],
    'õ': [[(0.85, 9.25), (1.25, 9.85), (1.625, 10.0), (2.525, 10.0), (2.875, 9.75), (3.0, 9.35), (3.0, 8.8), (2.875, 8.5), (2.75, 8.25), (2.375, 7.9), (1.5, 7.9)], [(2.375, 7.9), (2.5, 7.9), (2.875, 7.75), (3.1, 7.15), (3.1, 6.35), (2.875, 5.75), (2.5, 5.5), (1.35, 5.5), (1.0, 5.75), (0.75, 6.25)], [(0.0, 4.0), (4.0, 4.0)], [(2.75, -2.0), (2.75, 2.5), (0.875, -1.0), (3.375, -1.0)]],
    'ö': [[(0.0, 4.0), (4.0, 4.0)]],
    '÷': [[(1.25, 8.0), (2.375, 10.0), (2.375, 5.5)], [(0.0, 4.0), (4.0, 4.0)], [(2.75, -2.0), (2.75, 2.5), (0.875, -1.0), (3.375, -1.0)]],
    'ø': [[(1.25, 8.0), (2.375, 10.0), (2.375, 5.5)], [(0.0, 4.0), (4.0, 4.0)], [(1.125, 2.0), (1.375, 2.25), (1.725, 2.5), (2.5, 2.5), (2.875, 2.25), (3.0, 2.0), (3.125, 1.5), (3.125, 0.75), (2.975, 0.25), (2.625, 0.0), (1.5, -0.75), (1.125, -1.25), (0.875, -2.0), (3.125, -2.0), (3.125, -2.0)]],
    'ù': [[(0.0, 1.5), (4.0, 1.5)], [(1.0, 7.75), (1.625, 8.0), (2.375, 8.0), (2.875, 7.75), (3.125, 7.25), (3.25, 6.5), (3.25, 3.0)], [(3.25, 5.25), (3.0, 5.75), (2.5, 6.0), (1.625, 6.0), (1.125, 5.75), (0.875, 5.25), (0.75, 4.75), (0.75, 4.25), (0.875, 3.75), (1.125, 3.25), (1.625, 3.0), (2.5, 3.0), (3.0, 3.25), (3.25, 3.75)]],
    'ú': [[(0.0, 1.5), (4.0, 1.5)], [(0.75, 6.25), (0.875, 7.0), (1.25, 7.75), (1.75, 8.0), (2.25, 8.0), (2.75, 7.75), (3.125, 7.0), (3.25, 6.25), (3.25, 4.75), (3.125, 4.0), (2.75, 3.25), (2.25, 3.0), (1.75, 3.0), (1.25, 3.25), (0.875, 4.0), (0.75, 4.75), (0.75, 6.25)]],
    'û': [[(2.0, 6.0), (0.0, 3.0), (2.0, 0.0)], [(4.0, 6.0), (2.0, 3.0), (4.0, 0.0)]],
    'ü': [[(0.0, 6.0), (4.0, 6.0), (4.0, 0.0), (0.0, 0.0), (0.0, 6.0)]],
    'ý': [[(0.0, 6.0), (2.0, 3.0), (0.0, 0.0)], [(2.0, 6.0), (4.0, 3.0), (2.0, 0.0)]],
    'þ': [[(2.0, 7.5), (2.0, 2.0)], [(0.0, 4.75), (4.0, 4.75)], [(0.0, 0.75), (4.0, 0.75)]],
}

fonts = {
    48: stick_font,
}