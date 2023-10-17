import random

import arcade
import numpy as np
from HersheyFonts import HersheyFonts

from cursor.collection import Collection
from cursor.renderer import RealtimeRenderer
from tools.spline_experiment import transform_path

from tools.tests.lib import project

thefont = HersheyFonts()
thefont.load_default_font()
thefont.normalize_rendering(100)

text = [["1", "2", "3", "4"] * 8] * 32
char_bb = 50


def render(rr: RealtimeRenderer):
    rr.clear_list()
    collection = Collection()

    v1 = 0
    v2 = 0
    for line_idx, line in enumerate(text):
        for character_index, character in enumerate(line):
            temp_points = []

            for (x1, y1), (x2, y2) in thefont.lines_for_text(character):
                temp_points.append([[x1, -y1, 0], [x2, -y2, 0]])

            amp = 0.1
            v1 += random.uniform(-amp, amp)
            v2 += random.uniform(-amp, amp)

            basis1 = np.array([1, 0, 0])
            basis2 = np.array([0, 1, 0])

            plane_point = np.array([0, 0, 0])
            plane_normal = np.array([v1, v2, 1])

            c = project(temp_points, plane_point, plane_normal, basis1, basis2)

            bb = c.bb()
            for p in c:
                x1 = character_index * char_bb
                y1 = line_idx * char_bb
                x2 = x1 + char_bb
                y2 = y1 + char_bb
                collection.add(transform_path(p, bb, ((x1 - 10, y1), (x2 + 10, y2))))

    rr.add_collection(collection, line_width=2)


if __name__ == "__main__":
    rr = RealtimeRenderer(1600, 1600, "projection")
    rr.background(arcade.color.WHITE)

    rr.add_cb(arcade.key.N, render)
    rr.run()
