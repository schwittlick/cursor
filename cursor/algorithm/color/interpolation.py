import numpy as np


class ColorMath:
    @staticmethod
    def linear_srgb_to_oklab(
            c: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        l = 0.4122214708 * c[0] + 0.5363325363 * c[1] + 0.0514459929 * c[2]
        m = 0.2119034982 * c[0] + 0.6806995451 * c[1] + 0.1073969566 * c[2]
        s = 0.0883024619 * c[0] + 0.2817188376 * c[1] + 0.6299787005 * c[2]

        l_ = np.cbrt(l)
        m_ = np.cbrt(m)
        s_ = np.cbrt(s)

        return (
            0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
        )

    @staticmethod
    def oklab_to_linear_srgb(
            c: tuple[float, float, float]
    ) -> tuple[float, float, float]:
        l_ = c[0] + 0.3963377774 * c[1] + 0.2158037573 * c[2]
        m_ = c[0] - 0.1055613458 * c[1] - 0.0638541728 * c[2]
        s_ = c[0] - 0.0894841775 * c[1] - 1.2914855480 * c[2]

        l = l_ * l_ * l_
        m = m_ * m_ * m_
        s = s_ * s_ * s_

        return (
            +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
        )

    @staticmethod
    def lerp(
            v0: tuple[float, float, float],
            v1: tuple[float, float, float],
            percentage: float,
    ):
        x = (1 - percentage) * v0[0] + percentage * v1[0]
        y = (1 - percentage) * v0[1] + percentage * v1[1]
        z = (1 - percentage) * v0[2] + percentage * v1[2]
        return (x, y, z)

    @staticmethod
    def interpolate(
            c1_srgb: tuple[float, float, float],
            c2_srgb: tuple[float, float, float],
            perc: float,
            oklab: bool = True,
    ) -> tuple[float, float, float]:
        if oklab:
            c1_oklab = ColorMath.linear_srgb_to_oklab(c1_srgb)
            c2_oklab = ColorMath.linear_srgb_to_oklab(c2_srgb)
            interpolated = ColorMath.lerp(c1_oklab, c2_oklab, perc)
            interpolated = ColorMath.oklab_to_linear_srgb(interpolated)

        else:
            interpolated = ColorMath.lerp(c1_srgb, c2_srgb, perc)

        return interpolated
