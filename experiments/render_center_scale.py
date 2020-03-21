from cursor import path
import pyautogui


def center(pcol, dims):
    center = pcol.bb().center()
    center_dims = dims[0] / 2, dims[1] / 2
    diff = center_dims[0] - center[0], center_dims[1] - center[1]

    pcol.translate(diff[0], diff[1])


def scale(pcol, dims, padding=0):
    xfac = (dims[0] - padding * 2) / pcol.bb().w
    yfac = (dims[1] - padding * 2) / pcol.bb().h

    pcol.scale(xfac, yfac)


def test1():
    size = pyautogui.Size(1, 1)
    pcol = path.PathCollection(size)

    p1 = path.Path()
    p1.add(0.0, 0.0, 100)
    p1.add(0.4, 0.0, 100)
    p1.add(0.4, 0.4, 100)
    p1.add(0.0, 0.4, 100)

    pcol.add(p1, size)

    a3_size = (400, 400)

    scale(pcol, a3_size)
    center(pcol, a3_size)


def test2():
    size = pyautogui.Size(1, 1)
    pcol = path.PathCollection(size)

    p1 = path.Path()
    p1.add(0.1, 0.1, 100)
    p1.add(0.5, 0.1, 100)
    p1.add(0.5, 0.5, 100)
    p1.add(0.1, 0.5, 100)

    pcol.add(p1, size)

    a3_size = (400, 400)

    scale(pcol, a3_size)
    center(pcol, a3_size)

    print(pcol)
    print(pcol.bb())


def test3():
    size = pyautogui.Size(1920, 1080)
    pcol = path.PathCollection(size)

    p1 = path.Path()
    p1.add(0.1, 0.1, 100)
    p1.add(0.5, 0.1, 100)
    p1.add(0.5, 0.5, 100)
    p1.add(0.1, 0.5, 100)

    pcol.add(p1, size)

    a3_size = (800, 400)

    padding = 50
    scale(pcol, a3_size, padding=padding)
    center(pcol, a3_size)

    print(pcol)
    print(pcol.bb())


if __name__ == '__main__':
    test3()

    # gcode_renderer = renderer.CursorGCodeRenderer("test_scale")
    # gcode_renderer.render(pcol, "test_scale")
