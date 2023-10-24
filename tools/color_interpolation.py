from cursor import misc
from cursor.algorithm.color.copic import Copic, CopicColor, Color
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path
from cursor.properties import Property
from cursor.renderer.jpg import JpegRenderer


def create_theoretical_interpolation(c1: CopicColor, c2: CopicColor, width=100, oklab=True):
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


def create_interpolation(c1: CopicColor, c2: CopicColor, width=100, oklab=True):
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


if __name__ == '__main__':
    for i in range(30):
        c1 = Copic().random()
        c2 = Copic().random()

        dir = DataDirHandler().jpg("color_interpolation")

        copic_interpolation = create_interpolation(c1, c2, 1000, True)
        r = JpegRenderer(dir, w=1000, h=1000)
        r.add(copic_interpolation)
        r.render()
        r.save(f"interpolation_{c1.code.name}-{c2.code.name}_copic")

        theoretical_interpolation = create_theoretical_interpolation(c1, c2, 1000, True)
        r = JpegRenderer(dir, w=1000, h=1000)
        r.add(theoretical_interpolation)
        r.render()
        r.save(f"interpolation_{c1.code.name}-{c2.code.name}_theoretical")
