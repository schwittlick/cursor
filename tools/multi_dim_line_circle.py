"""
#python 2.x
"""
import numpy as np
import math
import matplotlib.pyplot as plt


class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


def sineAroundCircle(cx, cy, radius, amplitude, angle, frequency):
    p = Point()
    p.x = cx + (radius + amplitude * np.sin(frequency * angle)) * np.cos(angle)
    p.y = cy + (radius + amplitude * np.sin(frequency * angle)) * np.sin(angle)
    return p


cx = 150
cy = 150
radius = 100
amp = 10
frequency = 40
pt = Point()

fig, ax = plt.subplots()

for i in range(1, 360):
    angle = i * math.pi / 180
    pt = sineAroundCircle(cx, cy, radius, amp, angle, frequency)
    line1, = ax.plot(pt.x, pt.y, 'o')

frequency = 10
radius = 50
for i in range(1, 360):
    angle = i * math.pi / 180
    pt = sineAroundCircle(cx, cy, radius, amp, angle, frequency)
    line2, = ax.plot(pt.x, pt.y, 'o')

plt.show()
