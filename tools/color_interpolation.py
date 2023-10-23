from cursor import misc
from cursor.algorithm.color.color_enums import ColorCode
from cursor.algorithm.color.copic import Copic, CopicColor
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.path import Path, Property
from cursor.renderer.jpg import JpegRenderer


def lerp(v0, v1, t):
    x = (1 - t) * v0[0] + t * v1[0]
    y = (1 - t) * v0[1] + t * v1[1]
    z = (1 - t) * v0[2] + t * v1[2]
    return (x, y, z)


def interpolate_color(c1, c2, perc, oklab=True):
    c1_srgb = c1.as_srgb()
    c2_srgb = c2.as_srgb()
    if oklab:
        c1_oklab = CopicColor.linear_srgb_to_oklab(c1_srgb)
        c2_oklab = CopicColor.linear_srgb_to_oklab(c2_srgb)
        interpolated = lerp(c1_oklab, c2_oklab, perc)
        interpolated = CopicColor.oklab_to_linear_srgb(interpolated)

    else:
        interpolated = lerp(c1_srgb, c2_srgb, perc)

    interpolated_rgb = int(interpolated[0] * 255), int(interpolated[1] * 255), int(interpolated[2] * 255)

    return interpolated_rgb


def create_interpolation(c1: CopicColor, c2: CopicColor, width=100, oklab=True):
    c = Collection()
    for i in range(width):
        perc = misc.map(i, 0, width, 0, 1)
        rgb_interpolated = interpolate_color(c1, c2, perc, oklab)
        p = Path.from_tuple_list([(i, 0), (i, width)])
        p.properties[Property.WIDTH] = 1
        p.properties[Property.COLOR] = rgb_interpolated
        c.add(p)
    return c


if __name__ == '__main__':
    c1 = Copic().color(ColorCode.R29)
    c2 = Copic().color(ColorCode.Y06)

    dir = DataDirHandler().jpg("color_interpolation")

    r = JpegRenderer(dir, w=1000, h=1000)
    r.add(create_interpolation(c1, c2, 1000, True))
    r.render()
    r.save("test4_oklab")
