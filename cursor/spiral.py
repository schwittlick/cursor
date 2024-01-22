import math

from cursor.collection import Collection
from cursor.path import Path
from cursor.tools.realtime_boilerplate import RealtimeDropin


class WobblyFunction:
    def __init__(self):
        pass

    def generate(self, length: int) -> Collection:
        collection = Collection()

        path = Path()
        for i in range(length):
            path.add(i, self.val2((i / length) * math.pi, 0) )

        collection.add(path)
        return collection

    def val(self, x, t):
        return math.sin(3 * x + 3 * t + 5)

    def val2(self, x, t):
        return math.sin(2*x+3*t+5) + math.sin(3*x+2*t+4)


class Spiral:
    def __init__(self):
        self.theta = 0
        self.theta_incr = 0.02
        self.max_theta = 255
        self.r = 50
        self.xoffset = 0
        self.xoffset_incr = 0.55
        self.maxx = 1888

    def reset(self):
        self.theta = 0
        self.xoffset = 0

    def custom(self, pp):
        while self.theta < self.max_theta:
            y = self.r * math.cos(self.theta) * 2
            x = self.r * math.sin(self.theta) + self.xoffset
            pp.add(x, y, 0)
            self.theta += self.theta_incr
            self.xoffset += self.xoffset_incr
            if x >= self.maxx:
                break

        return pp

    def get_plain(self, pp):
        self.theta = 0
        self.theta_incr = 0.02
        self.max_theta = 255
        self.r = 50
        self.xoffset = 0
        self.xoffset_incr = 0.15
        self.maxx = 1888

        return self.custom(pp)


if __name__ == '__main__':
    wob = WobblyFunction()
    c = wob.generate(100)
    RealtimeDropin(c)
