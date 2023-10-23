from cursor.algorithm.color.copic import Copic, CopicColor
from cursor.algorithm.color.color_enums import ColorCode
from cursor.algorithm.color.spectral import spectral_mix


def test_simple_mix_spectral():
    c1 = Copic().color(ColorCode.B23)
    c2 = Copic().color(ColorCode.G17)

    mixed = spectral_mix(c1.rgb, c2.rgb, 0.5)

    print(mixed)


def lerp(v0, v1, t):
    x = (1 - t) * v0[0] + t * v1[0]
    y = (1 - t) * v0[1] + t * v1[1]
    z = (1 - t) * v0[2] + t * v1[2]
    return (x, y, z)


def test_simple_mix_oklab():
    c1 = Copic().color(ColorCode.B23)
    c2 = Copic().color(ColorCode.G17)

    print(c1.rgb)
    print(c2.rgb)

    c1_srgb = c1.as_srgb()
    c2_srgb = c2.as_srgb()

    print(c1_srgb)
    print(c2_srgb)

    c1_oklab = CopicColor.linear_srgb_to_oklab(c1_srgb)
    c2_oklab = CopicColor.linear_srgb_to_oklab(c2_srgb)

    print(c1_oklab)
    print(c2_oklab)

    interpolated_oklab = lerp(c1_oklab, c2_oklab, 0.5)
    print(interpolated_oklab)

    interpolated_srgb = CopicColor.oklab_to_linear_srgb(interpolated_oklab)
    print(interpolated_srgb)
