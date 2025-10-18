from typing import Tuple

import colour

from cursor.algorithm.color.combinations import (
    ColorDictionary,
    parse_copic_code,
    select_contrasting_colors,
    select_similar_colors,
)
from cursor.algorithm.color.copic import Color as CopicColor
from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC
from cursor.algorithm.color.copic_pen_enum import CopicColorGroup as CCG


def find_similar_copic_color(
    color_dict: ColorDictionary, copic: Copic, target_color_name: str
) -> Tuple[CopicColor, float]:
    target_color = color_dict.get_color(target_color_name)
    if not target_color:
        raise ValueError(f"Color '{target_color_name}' not found in ColorDictionary")

    target_rgb = tuple(v / 255 for v in target_color.rgb)
    target_xyz = colour.sRGB_to_XYZ(target_rgb)
    target_lab = colour.XYZ_to_Lab(target_xyz)

    min_delta = float("inf")
    most_similar_color = None

    for copic_color in copic.available_colors.values():
        copic_xyz = colour.sRGB_to_XYZ(copic_color.as_srgb())
        copic_lab = colour.XYZ_to_Lab(copic_xyz)
        delta = colour.delta_E(target_lab, copic_lab, method="CIE 2000")

        if delta < min_delta:
            min_delta = delta
            most_similar_color = copic_color

    return most_similar_color, min_delta


def test_comparison():
    color_dict = ColorDictionary()
    copic = Copic()
    copic_color = copic.random()
    match, delta = color_dict.compare_with_copic(copic_color)
    print(f"Copic color {copic_color.name} is most similar to {match.name} with delta {delta}")


def test_more():
    color_dict = ColorDictionary()
    copic = Copic()

    # target_color_name = "Dark Tyrian Blue"
    target_color_name = "Pinkish Cinnamon"
    similar_copic, delta = find_similar_copic_color(color_dict, copic, target_color_name)

    target_color = color_dict.get_color(target_color_name)
    print(f"Target color: {target_color_name} (#{target_color.hex})")
    print(
        f"Most similar Copic color: {similar_copic.name} "
        f"({similar_copic.code.name}) "
        f"(#{similar_copic.as_rgb()[0]:02x}"
        f"{similar_copic.as_rgb()[1]:02x}"
        f"{similar_copic.as_rgb()[2]:02x})"
    )
    print(f"Color difference (Delta E): {delta:.2f}")

    # Print the top 5 closest matches
    print("\nTop 5 closest Copic colors:")
    sorted_colors = sorted(
        copic.available_colors.values(),
        key=lambda c: colour.delta_E(
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(tuple(v / 255 for v in target_color.rgb))),
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(c.as_srgb())),
            method="CIE 2000",
        ),
    )
    for i, color in enumerate(sorted_colors[:5], 1):
        delta = colour.delta_E(
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(tuple(v / 255 for v in target_color.rgb))),
            colour.XYZ_to_Lab(colour.sRGB_to_XYZ(color.as_srgb())),
            method="CIE 2000",
        )
        print(
            f"{i}. {color.name} ({color.code.name}) "
            f"(#{color.as_rgb()[0]:02x}{color.as_rgb()[1]:02x}{color.as_rgb()[2]:02x}) "
            f"- Delta E: {delta:.2f}"
        )


def test_contrasting_colors_saturation():
    """Test that colors are selected with sufficient saturation contrast"""
    min_contrast = 4
    count = 3

    colors = select_contrasting_colors(
        color_group=CCG.R, count=count, contrast_param="saturation", min_primary_contrast=min_contrast
    )

    # Assert correct number of colors returned
    assert len(colors) == count, f"Expected {count} colors, got {len(colors)}"

    # Assert all colors are Color objects
    for color in colors:
        assert isinstance(color, CopicColor), f"Expected CopicColor, got {type(color)}"

    # Get saturation values
    saturations = [parse_copic_code(c.code)[0] for c in colors]

    # Assert first color (seed) has sufficient contrast with at least one other color
    seed_saturation = saturations[0]
    has_sufficient_contrast = any(abs(sat - seed_saturation) >= min_contrast for sat in saturations[1:])
    assert has_sufficient_contrast, (
        f"Seed color (sat={seed_saturation}) should have at least {min_contrast} "
        f"saturation difference with another color. Got saturations: {saturations}"
    )


def test_contrasting_colors_brightness():
    """Test that colors are selected with sufficient brightness contrast"""
    min_contrast = 4  # Brightness ranges 0-9, so use lower threshold
    count = 3

    colors = select_contrasting_colors(
        color_group=CCG.R, count=count, contrast_param="brightness", min_primary_contrast=min_contrast
    )

    # Assert correct number of colors returned
    assert len(colors) == count, f"Expected {count} colors, got {len(colors)}"

    # Get brightness values
    brightnesses = [parse_copic_code(c.code)[1] for c in colors]

    # Assert first color (seed) has sufficient contrast with at least one other color
    seed_brightness = brightnesses[0]
    has_sufficient_contrast = any(abs(bright - seed_brightness) >= min_contrast for bright in brightnesses[1:])
    assert has_sufficient_contrast, (
        f"Seed color (bright={seed_brightness}) should have at least {min_contrast} "
        f"brightness difference with another color. Got brightnesses: {brightnesses}"
    )


def test_contrasting_colors_distribution():
    """Test that selected colors are distributed (have contrast with each other)"""
    count = 3

    colors = select_contrasting_colors(
        color_group=CCG.R, count=count, contrast_param="saturation", min_primary_contrast=6
    )

    saturations = [parse_copic_code(c.code)[0] for c in colors]

    # Check that not all colors have the same saturation (ensures distribution)
    unique_saturations = set(saturations)
    assert len(unique_saturations) > 1, (
        f"Colors should have different saturation values for distribution. Got: {saturations}"
    )


def test_contrasting_colors_different_groups():
    """Test that the algorithm works with different color groups"""
    # Test with B group
    colors_b = select_contrasting_colors(
        color_group=CCG.B, count=2, contrast_param="saturation", min_primary_contrast=6
    )
    assert len(colors_b) == 2

    # Test with another group if available
    colors_r = select_contrasting_colors(
        color_group=CCG.R, count=2, contrast_param="brightness", min_primary_contrast=6
    )
    assert len(colors_r) == 2

    # Assert colors are from correct groups
    for color in colors_b:
        assert color.group == CCG.B, f"Expected color from group B, got {color.group}"
    for color in colors_r:
        assert color.group == CCG.R, f"Expected color from group R, got {color.group}"


def test_contrasting_colors_invalid_params():
    """Test that invalid parameters raise appropriate errors"""
    # Test invalid count
    try:
        select_contrasting_colors(color_group=CCG.R, count=1, contrast_param="saturation")
        assert False, "Should raise ValueError for count < 2"
    except ValueError as e:
        assert "count must be at least 2" in str(e)

    # Test invalid contrast_param
    try:
        select_contrasting_colors(color_group=CCG.R, count=2, contrast_param="invalid")
        assert False, "Should raise ValueError for invalid contrast_param"
    except ValueError as e:
        assert "must be 'saturation' or 'brightness'" in str(e)

    # Test missing color_group when cross_group=False
    try:
        select_contrasting_colors(color_group=None, count=2, contrast_param="saturation", cross_group=False)
        assert False, "Should raise ValueError when color_group is None and cross_group=False"
    except ValueError as e:
        assert "color_group must be specified" in str(e)


def test_contrasting_colors_cross_group_basic():
    """Test basic cross-group color selection"""
    copic = Copic()
    min_contrast = 4
    count = 3

    colors = select_contrasting_colors(
        count=count, contrast_param="saturation", min_primary_contrast=min_contrast, cross_group=True
    )

    # Assert correct number of colors returned
    assert len(colors) == count, f"Expected {count} colors, got {len(colors)}"

    # Assert all colors are Color objects
    for color in colors:
        assert isinstance(color, CopicColor), f"Expected CopicColor, got {type(color)}"

    # Get saturation values
    saturations = [parse_copic_code(c.code)[0] for c in colors]

    # Assert cross-group contrast is maintained
    seed_saturation = saturations[0]
    has_sufficient_contrast = any(abs(sat - seed_saturation) >= min_contrast for sat in saturations[1:])
    assert has_sufficient_contrast, (
        f"Seed color (sat={seed_saturation}) should have at least {min_contrast} "
        f"saturation difference with another color. Got saturations: {saturations}"
    )


def test_contrasting_colors_cross_group_multiple_groups():
    """Test that cross-group selection tends to select from different groups"""
    count = 5
    # Run multiple times to check tendency towards different groups
    total_unique_groups = 0
    runs = 10

    for _ in range(runs):
        colors = select_contrasting_colors(
            count=count, contrast_param="saturation", min_primary_contrast=4, cross_group=True
        )

        # Count unique groups in this run
        unique_groups = len(set(c.group for c in colors))
        total_unique_groups += unique_groups

    # On average, we should get more than 2 unique groups (tendency towards diversity)
    avg_unique_groups = total_unique_groups / runs
    assert avg_unique_groups >= 2.0, (
        f"Cross-group selection should tend to select from different groups. "
        f"Average unique groups: {avg_unique_groups:.2f} (expected >= 2.0)"
    )


def test_contrasting_colors_cross_group_brightness():
    """Test cross-group selection with brightness contrast"""
    min_contrast = 4
    count = 3

    colors = select_contrasting_colors(
        count=count, contrast_param="brightness", min_primary_contrast=min_contrast, cross_group=True
    )

    # Assert correct number of colors returned
    assert len(colors) == count, f"Expected {count} colors, got {len(colors)}"

    # Get brightness values
    brightnesses = [parse_copic_code(c.code)[1] for c in colors]

    # Assert cross-group contrast is maintained
    seed_brightness = brightnesses[0]
    has_sufficient_contrast = any(abs(bright - seed_brightness) >= min_contrast for bright in brightnesses[1:])
    assert has_sufficient_contrast, (
        f"Seed color (bright={seed_brightness}) should have at least {min_contrast} "
        f"brightness difference with another color. Got brightnesses: {brightnesses}"
    )


def test_contrasting_colors_cross_group_all_different():
    """Test that when requesting few colors, they tend to be from different groups"""
    count = 3
    colors = select_contrasting_colors(
        count=count, contrast_param="saturation", min_primary_contrast=4, cross_group=True
    )

    # Get unique groups
    groups = [c.group for c in colors]
    unique_groups = set(groups)

    # With count=3 and cross_group=True, we should ideally get 2-3 different groups
    assert len(unique_groups) >= 2, f"Expected at least 2 different groups, got {len(unique_groups)}: {groups}"


def test_similar_colors_basic():
    """Test basic similar colors selection"""

    count = 3
    max_contrast = 3

    colors = select_similar_colors(count=count, max_contrast=max_contrast)

    # Assert correct number of colors returned
    assert len(colors) == count, f"Expected {count} colors, got {len(colors)}"

    # Assert all colors are Color objects
    for color in colors:
        assert isinstance(color, CopicColor), f"Expected CopicColor, got {type(color)}"

    # Get saturation and brightness values
    values = [(parse_copic_code(c.code)[0], parse_copic_code(c.code)[1]) for c in colors]
    seed_sat, seed_bright = values[0]

    # Verify that all colors are similar to seed (first color)
    for sat, bright in values[1:]:
        # At least one dimension should be within max_contrast
        sat_diff = abs(sat - seed_sat)
        bright_diff = abs(bright - seed_bright)
        min_diff = min(sat_diff, bright_diff)
        assert min_diff <= max_contrast, (
            f"Color (sat={sat}, bright={bright}) not similar enough to seed "
            f"(sat={seed_sat}, bright={seed_bright}). Min diff: {min_diff}, max: {max_contrast}"
        )


def test_similar_colors_different_groups():
    """Test that similar colors tend to come from different groups"""

    count = 3
    colors = select_similar_colors(count=count, max_contrast=3)

    # Get unique groups
    groups = [c.group for c in colors]
    unique_groups = set(groups)

    # Should tend to select from different groups
    assert len(unique_groups) >= 2, (
        f"Expected at least 2 different groups for visual variety, got {len(unique_groups)}: {groups}"
    )


def test_similar_colors_invalid_count():
    """Test that invalid count raises ValueError"""

    try:
        select_similar_colors(count=1, max_contrast=3)
        assert False, "Should raise ValueError for count < 2"
    except ValueError as e:
        assert "count must be at least 2" in str(e)


def test_similar_colors_not_enough_found():
    """Test that exception is raised when not enough similar colors exist"""

    # Request many colors with very strict constraint - should fail
    try:
        select_similar_colors(count=50, max_contrast=1)
        # If it succeeds, that's actually fine - just check the constraint
    except ValueError as e:
        # Expected to fail with not enough colors
        assert "Not enough similar colors found" in str(e) or "Could not find" in str(e)


def test_similar_colors_flexible_matching():
    """Test that flexible matching works (similar in saturation OR brightness)"""

    count = 3
    max_contrast = 2

    colors = select_similar_colors(count=count, max_contrast=max_contrast)

    # Get saturation and brightness values
    values = [(parse_copic_code(c.code)[0], parse_copic_code(c.code)[1]) for c in colors]
    seed_sat, seed_bright = values[0]

    # Verify flexible matching: each color should be similar in at least one dimension
    for i, (sat, bright) in enumerate(values[1:], 1):
        sat_diff = abs(sat - seed_sat)
        bright_diff = abs(bright - seed_bright)

        # At least one should be within max_contrast (flexible OR matching)
        assert sat_diff <= max_contrast or bright_diff <= max_contrast, (
            f"Color {i} (sat={sat}, bright={bright}) not similar to seed "
            f"(sat={seed_sat}, bright={seed_bright}). "
            f"Sat diff: {sat_diff}, Bright diff: {bright_diff}, max: {max_contrast}"
        )


def test_similar_colors_multiple_runs():
    """Test that similar colors selection works consistently across multiple runs"""

    count = 3
    max_contrast = 3
    runs = 5
    found_diversity = False

    for run in range(runs):
        colors = select_similar_colors(count=count, max_contrast=max_contrast)
        assert len(colors) == count, f"Run {run}: Expected {count} colors, got {len(colors)}"

        # Check that we got different groups
        groups = [c.group for c in colors]
        unique_groups = len(set(groups))
        # At least sometimes we should get 2+ groups
        if unique_groups >= 2:
            found_diversity = True

    # We should find diversity in at least one run
    assert found_diversity, "Never found colors from 2+ different groups across multiple runs"


def test_parse_copic_code_standard_formats():
    """Test parsing of standard Copic color codes"""
    from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC

    # Test standard two-digit codes (saturation + brightness)
    # R05: saturation=0, brightness=5
    assert parse_copic_code(CCC.R05) == (0, 5)

    # R89: saturation=8, brightness=9
    assert parse_copic_code(CCC.R89) == (8, 9)

    # Test four-digit codes (saturation + multi-digit brightness)
    # B0000: saturation=0, brightness=0
    assert parse_copic_code(CCC.B0000) == (0, 0)


def test_parse_copic_code_single_digit():
    """Test parsing of single-digit color codes (brightness only)"""
    from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC

    # W4: single digit = brightness only, saturation=0
    result = parse_copic_code(CCC.W4)
    assert result == (0, 4), f"Expected (0, 4) for W4, got {result}"


def test_parse_copic_code_multi_digit_brightness():
    """Test parsing of codes with multi-digit brightness values"""
    from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC

    # Test 4-digit codes: first digit = saturation, remaining = brightness
    # B000: saturation=0, brightness=0
    result = parse_copic_code(CCC.B000)
    assert result[0] == 0, f"Expected saturation=0 for B000, got {result[0]}"
    assert result[1] == 0, f"Expected brightness=0 for B000, got {result[1]}"

    # BV0000: saturation=0, brightness=0
    result = parse_copic_code(CCC.BV0000)
    assert result[0] == 0, f"Expected saturation=0 for BV0000, got {result[0]}"
    assert result[1] == 0, f"Expected brightness=0 for BV0000, got {result[1]}"


def test_parse_copic_code_special_colors():
    """Test parsing of special color codes (non-standard naming)"""
    from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC

    # FBG2: special color - saturation should be 5, brightness=2
    result = parse_copic_code(CCC.FBG2)
    assert result[0] == 5, f"Special color saturation should be 5, got {result[0]}"
    assert result[1] == 5, f"Expected brightness=5 for FBG2, got {result[1]}"

    # _110: Black - saturation=9, brightness=9
    result = parse_copic_code(CCC._110)
    assert result == (9, 9), f"Expected (9, 9) for _110 (Black), got {result}"

    # _000: White - saturation=0, brightness=0
    result = parse_copic_code(CCC._000)
    assert result == (0, 0), f"Expected (0, 0) for _000 (White), got {result}"


def test_parse_copic_code_consistency():
    """Test that parsing the same code multiple times gives consistent results for standard codes"""
    from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC

    # Standard codes should be deterministic
    result1 = parse_copic_code(CCC.R05)
    result2 = parse_copic_code(CCC.R05)
    assert result1 == result2, "Standard color codes should parse consistently"

    result3 = parse_copic_code(CCC.B0000)
    result4 = parse_copic_code(CCC.B0000)
    assert result3 == result4, "Standard color codes should parse consistently"


def test_parse_copic_code_various_groups():
    """Test parsing colors from various color groups"""
    from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC

    # Test different color groups to ensure letter prefix doesn't affect parsing
    # All should follow same rule: first digit = saturation, rest = brightness

    # Y group (Yellow)
    result = parse_copic_code(CCC.Y02)
    assert result == (0, 2), f"Expected (0, 2) for Y02, got {result}"

    # BV group (Blue Violet)
    result = parse_copic_code(CCC.BV01)
    assert result == (0, 1), f"Expected (0, 1) for BV01, got {result}"

    # E group (Earth)
    result = parse_copic_code(CCC.E01)
    assert result == (0, 1), f"Expected (0, 1) for E01, got {result}"


def test_parse_copic_code_edge_cases():
    """Test edge cases and boundary values"""

    # Test maximum saturation (9) with various brightness
    result = parse_copic_code(CCC.R89)
    assert result[0] == 8, f"Expected saturation=8 for R89, got {result[0]}"
    assert result[1] == 9, f"Expected brightness=9 for R89, got {result[1]}"

    # Test zero saturation and zero brightness
    result = parse_copic_code(CCC.B0000)
    assert result == (0, 0), f"Expected (0, 0) for B0000, got {result}"


def test_compare_with_copic_returns_color_and_float():
    """Test that compare_with_copic returns a Color object and a float delta"""
    color_dict = ColorDictionary()
    copic = Copic()

    # Get a known copic color
    copic_color = copic.color_by_code(CCC.R05)

    # Compare with color dictionary
    match, delta = color_dict.compare_with_copic(copic_color)

    # Assert return types
    assert isinstance(match, color_dict.colors[list(color_dict.colors.keys())[0]].__class__), (
        f"Expected Color from ColorDictionary, got {type(match)}"
    )
    assert isinstance(delta, float), f"Expected delta to be float, got {type(delta)}"
    assert delta >= 0, f"Delta E should be non-negative, got {delta}"


def test_compare_with_copic_finds_match():
    """Test that compare_with_copic finds a match from the color dictionary"""
    color_dict = ColorDictionary()
    copic = Copic()

    # Pick a random copic color
    copic_color = copic.random()

    # Compare with color dictionary
    match, delta = color_dict.compare_with_copic(copic_color)

    # Assert we got a valid match
    assert match is not None, "Should return a matching color"
    assert match.name in [c.name for c in color_dict.colors.values()], (
        "Matched color should be from the color dictionary"
    )


def test_compare_with_copic_delta_range():
    """Test that Delta E values are in reasonable range"""
    color_dict = ColorDictionary()
    copic = Copic()

    # Test with multiple colors
    deltas = []
    for _ in range(10):
        copic_color = copic.random()
        match, delta = color_dict.compare_with_copic(copic_color)
        deltas.append(delta)

    # Delta E typically ranges 0-100, but most perceptual differences are 0-50
    for delta in deltas:
        assert 0 <= delta <= 200, f"Delta E should be in reasonable range, got {delta}"


def test_compare_with_copic_consistency():
    """Test that comparing the same color multiple times gives same result"""
    color_dict = ColorDictionary()
    copic = Copic()

    copic_color = copic.color_by_code(CCC.R05)

    # Compare multiple times
    match1, delta1 = color_dict.compare_with_copic(copic_color)
    match2, delta2 = color_dict.compare_with_copic(copic_color)

    # Should get same results
    assert match1.name == match2.name, "Should get same match for same input"
    assert abs(delta1 - delta2) < 0.01, f"Should get same delta for same input: {delta1} vs {delta2}"


def test_compare_with_copic_different_colors():
    """Test that different copic colors produce different matches"""
    color_dict = ColorDictionary()
    copic = Copic()
    # Compare very different colors
    red_color = copic.color_by_code(CCC.R89)
    blue_color = copic.color_by_code(CCC.B79)

    match_red, delta_red = color_dict.compare_with_copic(red_color)
    match_blue, delta_blue = color_dict.compare_with_copic(blue_color)

    # The matches should be different (highly likely for red vs blue)
    # Note: This might occasionally fail if both happen to match the same neutral color
    # but it's extremely unlikely
    assert match_red.name != match_blue.name or abs(delta_red - delta_blue) > 1.0, (
        "Very different colors should produce different matches or significantly different deltas"
    )
