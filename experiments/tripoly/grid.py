from cursor import path
from cursor import misc
import math


def PointsInCircum(r, n=100):
    return [
        (
            math.cos(2 * (math.pi - math.pi / 2) / n * x) * r,
            math.sin(2 * (math.pi - math.pi / 2) / n * x) * r,
        )
        for x in range(0, n + 1)
    ]


class Triangle:
    def __init__(self, x1, y1, x2, y2, x3, y3, rot=False) -> None:
        self.points = []
        self.points.append(path.TimedPosition(x1, y1))
        self.points.append(path.TimedPosition(x2, y2))
        self.points.append(path.TimedPosition(x3, y3))

        for point in self.points:
            point.rot(math.pi / 2)

        if rot:
            for point in self.points:
                point.rot(math.pi)

    def translate(self, x, y):
        for point in self.points:
            point.translate(x, y)

    def to_path(self) -> path.Path:
        p = path.Path()
        for point in self.points:
            p.add(point.x, point.y)

        p.add(self.points[0].x, self.points[0].y)

        return p


def triangleGrid():
    fff = 172
    c = path.PathCollection()
    for i in range(8):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff, 0)
        c.add(pa.copy())

    for i in range(7):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86, -150)
        c.add(pa.copy())

    for i in range(6):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86 * 2, -150 * 2)
        c.add(pa.copy())

    for i in range(5):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86 * 3, -150 * 3)
        c.add(pa.copy())

    for i in range(4):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86 * 4, -150 * 4)
        c.add(pa.copy())

    for i in range(3):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86 * 5, -150 * 5)
        c.add(pa.copy())

    for i in range(2):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86 * 6, -150 * 6)
        c.add(pa.copy())

    for i in range(1):
        triangle = Triangle(100, 0, -50, 86.6, -50, -86.6, True)
        pa = triangle.to_path()
        pa.translate(i * fff + 86 * 7, -150 * 7)
        c.add(pa.copy())

    misc.save_wrapper(c, "tripoly", "grid_one2")


if __name__ == "__main__":
    triangleGrid()
