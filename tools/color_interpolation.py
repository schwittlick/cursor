import logging

from cursor import misc
from cursor.algorithm.color.color_enums import ColorCode
from cursor.algorithm.color.copic import Copic, CopicColor, Color
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import PlotterType, PaperSize
from cursor.export import ExportWrapper
from cursor.path import Path
from cursor.properties import Property
from cursor.renderer.hpgl import HPGLRenderer
from cursor.renderer.jpg import JpegRenderer

import random


def create_theoretical_interpolation(c1: CopicColor, c2: CopicColor, width=100, oklab=True) -> Collection:
    c = Collection()
    for i in range(width):
        perc = misc.map(i, 0, width, 0, 1)
        srgb_interpolated = Color.interpolate(c1.as_srgb(), c2.as_srgb(), perc, oklab)
        rgb_interpolated = int(srgb_interpolated[0] * 255), int(srgb_interpolated[1] * 255), int(
            srgb_interpolated[2] * 255)

        p = Path.from_tuple_list([(i, 0), (i, width)])
        p.properties[Property.WIDTH] = 1
        p.properties[Property.COLOR] = rgb_interpolated
        c.add(p)
    return c


def create_interpolation(c1: CopicColor, c2: CopicColor, width=100, oklab=True) -> Collection:
    c = Collection()
    for i in range(width):
        perc = misc.map(i, 0, width, 0, 1)
        srgb_interpolated = Color.interpolate(c1.as_srgb(), c2.as_srgb(), perc, oklab)
        rgb_interpolated = int(srgb_interpolated[0] * 255), int(srgb_interpolated[1] * 255), int(
            srgb_interpolated[2] * 255)

        most_similar_copic_color = Copic().most_similar(rgb_interpolated)
        # print(most_similar_copic_color)

        p = Path.from_tuple_list([(i, 0), (i, width)])
        p.properties[Property.WIDTH] = 1
        p.properties[Property.COLOR] = most_similar_copic_color.rgb  # rgb_interpolated
        c.add(p)
    return c


def calc_copic_color_batches(c1: CopicColor, c2: CopicColor, width=100, oklab=True) -> list[CopicColor]:
    batches = []
    for i in range(width):
        perc = misc.map(i, 0, width, 0, 1)
        srgb_interpolated = Color.interpolate(c1.as_srgb(), c2.as_srgb(), perc, oklab)
        rgb_interpolated = int(srgb_interpolated[0] * 255), int(srgb_interpolated[1] * 255), int(
            srgb_interpolated[2] * 255)

        most_similar_copic_color = Copic().most_similar(rgb_interpolated)
        batches.append(most_similar_copic_color)

    return batches


class ColorBand:
    def __init__(self, color_code, min_idx, max_idx, median):
        self.color_code = color_code
        self.min_idx = min_idx
        self.max_idx = max_idx
        self.median = median
        self.prev: [None, ColorBand] = None
        self.next: [None, ColorBand] = None

    def __repr__(self):
        return f"{self.color_code}, {self.min_idx}->{self.max_idx}, median={self.median}. prev={self.prev} next={self.next}"


def find_fitting_bound(color_bounds: list, index: int) -> ColorBand:
    for idx, bound in enumerate(color_bounds):
        if bound[1] <= index <= bound[2]:
            cb = ColorBand(bound[0], bound[1], bound[2], bound[3])
            if idx > 0:
                prev_bounds = color_bounds[idx - 1]
                cb.prev = ColorBand(prev_bounds[0], prev_bounds[1], prev_bounds[2], prev_bounds[3])
            if idx < len(color_bounds) - 1:
                next_bounds = color_bounds[idx + 1]
                cb.next = ColorBand(next_bounds[0], next_bounds[1], next_bounds[2], next_bounds[3])
            return cb


def create_concrete_interpolation(c1: CopicColor, c2: CopicColor, width=100, oklab=True) -> Collection:
    batches = calc_copic_color_batches(c1, c2, width, oklab)
    indices_dict = {}
    for idx, color in enumerate(batches):
        if color.code not in indices_dict.keys():
            indices_dict[color.code] = [idx]
        else:
            indices_dict[color.code].append(idx)

    color_bounds = []
    for color_code, index_list in indices_dict.items():
        min_index = min(index_list)
        max_index = max(index_list)
        color_bounds.append((color_code, min_index, max_index, misc.lerp(min_index, max_index, 0.5)))

    c = Collection(name=f"{c1.code.name}_{c2.code.name}")
    color_coordinates = {}

    for i in range(width):
        bound = find_fitting_bound(color_bounds, i)
        percentage = None
        from_color = None
        to_color = None
        if bound.prev and bound.next:
            if i < bound.median:
                percentage = 1 - misc.inv_lerp(bound.prev.median, bound.median, i)
                from_color = bound.prev.color_code
                to_color = bound.color_code
            else:
                percentage = 1 - misc.inv_lerp(bound.median, bound.next.median, i)
                from_color = bound.color_code
                to_color = bound.next.color_code
        elif bound.prev and not bound.next:
            if i < bound.median:
                percentage = 1 - misc.inv_lerp(bound.prev.median, bound.median, i)
                from_color = bound.prev.color_code
                to_color = bound.color_code
            else:
                percentage = 1  # use current color
                from_color = bound.color_code
                to_color = bound.color_code
        elif not bound.prev and bound.next:
            if i > bound.median:
                percentage = 1 - misc.inv_lerp(bound.median, bound.next.median, i)
                from_color = bound.color_code
                to_color = bound.next.color_code
            else:
                percentage = 1  # use current color
                from_color = bound.color_code
                to_color = bound.color_code
        elif not bound.next and not bound.prev:
            # same-color gradient (actually not a gradient)
            percentage = 1
            from_color = bound.color_code
            to_color = bound.color_code

        if not percentage:
            logging.error(f"How is this possible")
            logging.error(f"{c1} + {c2}")

        for y in range(width):  # height
            chosen_color = random.choices([from_color, to_color], weights=(percentage, 1 - percentage), k=1)[0]

            if chosen_color not in color_coordinates.keys():
                color_coordinates[chosen_color] = [(i, y)]
            else:
                color_coordinates[chosen_color].append((i, y))

    logging.info(f"{len(color_coordinates.keys())} different colors")

    pen_index = 1
    for color, coordinates in color_coordinates.items():
        for coordinate in coordinates:
            pixel = Path.from_tuple_list([(coordinate[0], coordinate[1]), (coordinate[0], coordinate[1])])
            pixel.properties[Property.COLOR] = Copic().color(color).rgb
            pixel.properties[Property.WIDTH] = 1
            pixel.properties[Property.PEN_SELECT] = pen_index
            c.add(pixel)

        pen_index += 1

    return c


if __name__ == '__main__':
    """
    The next step is to mix a line color by separating dots
    check the distance of a colored line from the centroid
    
    imagine we have batches of interpolated colors, like a length?
    0 - 1000 total image
    0 - 150 color1 ~ middle is 75
    150 - 350 color2 ~ middle = lerp(150, 350, 0.5)
    350 - 750 color 3 ~ lerp(350, 750, 0.5)
    750 - 1000 color4 ~ lerp(750, 1000, 0.5)
    
    example
    we are at a color at position 200
    we want the percentage between color2 and color3
    percentage = inv_lerp(150, 300, 200)
    percentage = 0.3 (approximated)
    that means at color position 200 we want a 1-0.3 probability 
    for each segment of a line to be of color 2 and a 0.3 probability to be color 3
    
    
    """

    size = 50

    for i in range(1):
        # c1 = Copic().random()
        # c2 = Copic().random()
        c1 = Copic().color(ColorCode.B39)
        c2 = Copic().color(ColorCode.G14)

        logging.info(f"{c1} -> {c2}")

        dir = DataDirHandler().jpg("color_interpolation")
        dir_hpgl = DataDirHandler().hpgl("color_interpolation")

        concrete_interpolation = create_concrete_interpolation(c1, c2, size, True)

        ExportWrapper().ex(
            concrete_interpolation,
            PlotterType.HP_7550A,
            PaperSize.LANDSCAPE_A3,
            80,
            "color_interpolation",
            f"{concrete_interpolation.name}",
            keep_aspect_ratio=True,
        )

        continue

        hpgl_renderer = HPGLRenderer(dir_hpgl)
        hpgl_renderer.render(concrete_interpolation)
        hpgl_renderer.save(f"interpolation_{c1.code.name}-{c2.code.name}_concrete")

        r = JpegRenderer(dir, w=size, h=size)
        r.add(concrete_interpolation)
        r.render()
        r.save(f"interpolation_{c1.code.name}-{c2.code.name}_concrete")

        copic_interpolation = create_interpolation(c1, c2, size, True)
        r = JpegRenderer(dir, w=size, h=size)
        r.add(copic_interpolation)
        r.render()
        r.save(f"interpolation_{c1.code.name}-{c2.code.name}_copic")

        theoretical_interpolation = create_theoretical_interpolation(c1, c2, size, True)
        r = JpegRenderer(dir, w=size, h=size)
        r.add(theoretical_interpolation)
        r.render()
        r.save(f"interpolation_{c1.code.name}-{c2.code.name}_theoretical")
