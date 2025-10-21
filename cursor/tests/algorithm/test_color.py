from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.algorithm.color.interpolation import ColorMath
from cursor.algorithm.color.spectral import spectral_mix


def test_simple_mix_spectral():
    c1 = Copic().color_by_code(CopicColorCode.B23)
    c2 = Copic().color_by_code(CopicColorCode.Y06)

    mixed = spectral_mix(c1.as_rgb(), c2.as_rgb(), 0.5)

    # Assert result is a valid RGB tuple
    assert len(mixed) == 3, "Mixed color should be an RGB 3-tuple"
    assert all(0 <= val <= 255 for val in mixed), "RGB values should be in range [0, 255]"
    assert all(isinstance(val, int) for val in mixed), "RGB values should be integers"

    # At 0% and 100%, should return the original colors (as lists)
    mixed_0 = spectral_mix(c1.as_rgb(), c2.as_rgb(), 0.0)
    assert mixed_0 == list(c1.as_rgb()), "At 0%, should return first color"

    mixed_100 = spectral_mix(c1.as_rgb(), c2.as_rgb(), 1.0)
    assert mixed_100 == list(c2.as_rgb()), "At 100%, should return second color"


def test_simple_mix_oklab():
    c1 = Copic().color_by_code(CopicColorCode.B23)
    c2 = Copic().color_by_code(CopicColorCode.Y06)

    c1_srgb = c1.as_srgb()
    c2_srgb = c2.as_srgb()

    # Test sRGB format
    assert len(c1_srgb) == 3, "sRGB should be a 3-tuple"
    assert len(c2_srgb) == 3, "sRGB should be a 3-tuple"
    assert all(0 <= val <= 1 for val in c1_srgb), "sRGB values should be in range [0, 1]"
    assert all(0 <= val <= 1 for val in c2_srgb), "sRGB values should be in range [0, 1]"

    # Test conversion to Oklab
    c1_oklab = ColorMath.linear_srgb_to_oklab(c1_srgb)
    c2_oklab = ColorMath.linear_srgb_to_oklab(c2_srgb)

    assert len(c1_oklab) == 3, "Oklab should be a 3-tuple"
    assert len(c2_oklab) == 3, "Oklab should be a 3-tuple"
    assert all(isinstance(val, (int, float)) for val in c1_oklab), "Oklab values should be numeric"

    # Test interpolation
    interpolated_oklab = ColorMath.lerp(c1_oklab, c2_oklab, 0.5)
    assert len(interpolated_oklab) == 3, "Interpolated Oklab should be a 3-tuple"

    # Test conversion back to sRGB
    interpolated_srgb = ColorMath.oklab_to_linear_srgb(interpolated_oklab)
    assert len(interpolated_srgb) == 3, "Converted sRGB should be a 3-tuple"
    assert all(isinstance(val, (int, float)) for val in interpolated_srgb), "sRGB values should be numeric"

    # Test roundtrip: sRGB -> Oklab -> sRGB should be close to original
    roundtrip = ColorMath.oklab_to_linear_srgb(c1_oklab)
    assert all(abs(a - b) < 0.001 for a, b in zip(c1_srgb, roundtrip)), "Roundtrip conversion should preserve color"


def test_gradient():
    c1 = Copic().color_by_code(CopicColorCode.B23)
    c2 = Copic().color_by_code(CopicColorCode.Y06)

    steps = 50
    gradient = ColorMath.calc_gradient(c1, c2, steps, True)

    # Basic assertions
    assert len(gradient) == steps + 1, f"Gradient should have {steps + 1} colors (including start and end)"
    assert all(hasattr(color, "as_srgb") for color in gradient), "All gradient elements should be Color objects"

    # First and last colors should match input colors (when clamped to copic)
    assert gradient[0] == c1, "First color in gradient should match start color"
    assert gradient[-1] == c2, "Last color in gradient should match end color"

    # All colors should be valid Copic colors when clamped
    assert all(color.is_copic() for color in gradient), "All gradient colors should be Copic colors when clamped"

    # Test without clamping to Copic
    gradient_unclamped = ColorMath.calc_gradient(c1, c2, steps, False)
    assert len(gradient_unclamped) == steps + 1, "Unclamped gradient should have correct length"

    # Test with random colors
    for i in range(3):  # Reduced from 10 to 3 for faster tests
        c1_random = Copic().random()
        c2_random = Copic().random()
        gradient_random = ColorMath.calc_gradient(c1_random, c2_random, 20, True)

        assert len(gradient_random) == 21, "Random gradient should have correct length"
        assert gradient_random[0] == c1_random, "Random gradient should start with first color"
        assert gradient_random[-1] == c2_random, "Random gradient should end with second color"

        # Check for some variety in the gradient (not all the same color unless c1 == c2)
        if c1_random != c2_random:
            gradient_unique = [v for i, v in enumerate(gradient_random) if i == 0 or v != gradient_random[i - 1]]
            assert len(gradient_unique) > 1, "Gradient should have at least some variation when colors differ"
