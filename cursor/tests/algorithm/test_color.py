from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.algorithm.color.interpolation import ColorMath
from cursor.algorithm.color.spectral import spectral_mix


def test_simple_mix_spectral():
    c1 = Copic().color_by_code(CopicColorCode.B23)
    c2 = Copic().color_by_code(CopicColorCode.Y06)

    mixed = spectral_mix(c1.as_rgb(), c2.as_rgb(), 0.5)

    print(mixed)


def lerp(v0, v1, t):
    x = (1 - t) * v0[0] + t * v1[0]
    y = (1 - t) * v0[1] + t * v1[1]
    z = (1 - t) * v0[2] + t * v1[2]
    return (x, y, z)


def test_simple_mix_oklab():
    c1 = Copic().color_by_code(CopicColorCode.B23)
    c2 = Copic().color_by_code(CopicColorCode.Y06)

    print(c1.as_rgb())
    print(c2.as_rgb())

    c1_srgb = c1.as_srgb()
    c2_srgb = c2.as_srgb()

    print(c1_srgb)
    print(c2_srgb)

    c1_oklab = ColorMath.linear_srgb_to_oklab(c1_srgb)
    c2_oklab = ColorMath.linear_srgb_to_oklab(c2_srgb)

    print(c1_oklab)
    print(c2_oklab)

    interpolated_oklab = lerp(c1_oklab, c2_oklab, 0.5)
    print(interpolated_oklab)

    interpolated_srgb = ColorMath.oklab_to_linear_srgb(interpolated_oklab)
    print(interpolated_srgb)


def test_gradient():
    c1 = Copic().color_by_code(CopicColorCode.B23)
    c2 = Copic().color_by_code(CopicColorCode.Y06)

    for i in range(10):

        gradient = ColorMath.calc_gradient(c1, c2, 50, True)
        gradient_unique = [v for i, v in enumerate(gradient) if i == 0 or v != gradient[i - 1]]
        # print(gradient)
        # print(gradient_unique)
        print(len(gradient_unique))
        print(c1)
        print(c2)
        c1 = Copic().random()
        c2 = Copic().random()
