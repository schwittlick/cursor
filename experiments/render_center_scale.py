from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

import pyautogui

def center(pcol, dims):
    center = pcol.bb().center()
    center_dims = dims[0] / 2, dims[1] / 2
    diff = center_dims[0] - center[0], center_dims[1] - center[1]
    #new_center = center[0] + diff[0], center[1] + diff[1]

    print(pcol)
    print(pcol.bb())
    pcol.translate(diff[0], diff[1])
    print(pcol)
    print(pcol.bb())

def scale(pcol, dims):
    xfac = dims[0] / pcol.bb().w
    yfac = dims[1] / pcol.bb().h

    print(pcol)
    print(pcol.bb())
    pcol.scale(xfac, yfac)
    print(pcol)
    print(pcol.bb())


if __name__ == '__main__':
    size = pyautogui.Size(1920, 1080)
    pcol = path.PathCollection(size)

    p1 = path.Path()
    p1.add(0.0, 0.0, 100)
    p1.add(0.4, 0.0, 100)
    p1.add(0.4, 0.4, 100)
    p1.add(0.0, 0.4, 100)

    pcol.add(p1, size)

    a3_size = (400, 400)

    padding = 50
    scale(pcol, a3_size, padding)
    center(pcol, a3_size)

    #gcode_renderer = renderer.CursorGCodeRenderer("test_scale")
    #gcode_renderer.render(pcol, "test_scale")