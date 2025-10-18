import json
import pathlib
import random

import colour

from cursor.algorithm.color.copic import Color as CopicColor
from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC
from cursor.algorithm.color.copic_pen_enum import CopicColorGroup as CCG


class Color:
    def __init__(self, name: str, hex: str, rgb: list[int], lab: list[float], cmyk: list[int], combinations: list[int]):
        self.name = name
        self.hex = hex
        self.rgb = tuple(rgb)
        self.lab = tuple(lab)
        self.cmyk = tuple(cmyk)
        self.combinations = combinations

    def as_srgb(self) -> tuple[float, ...]:
        return tuple(v / 255 for v in self.rgb)


class ColorDictionary:
    """
    Loading the combintations from the book
    A Dictionary of Color Combinations, 2011, Seigensha Art Publishing
    """

    def __init__(self):
        self.colors: dict[str, Color] = {}

        data_path = pathlib.Path(__file__).parent / "data" / "color_dictionary.json"
        self.load_colors(data_path.as_posix())

    def load_colors(self, json_file: str):
        with open(json_file, "r") as f:
            color_data = json.load(f)

        for color in color_data:
            self.colors[color["name"]] = Color(
                name=color["name"],
                hex=color["hex"],
                rgb=color["rgb"],
                lab=color["lab"],
                cmyk=color["cmyk"],
                combinations=color.get("combinations", []),
            )

    def get_color(self, name: str) -> Color | None:
        return self.colors.get(name)

    def most_similar(self, target_color: tuple[float, ...]) -> Color:
        target_cie = colour.sRGB_to_XYZ(target_color)

        min_delta = float("inf")
        most_similar_color = None

        for color in self.colors.values():
            color_cie = colour.sRGB_to_XYZ(color.as_srgb())
            delta = colour.delta_E(target_cie, color_cie)

            if delta < min_delta:
                min_delta = delta
                most_similar_color = color

        return most_similar_color  # type: ignore

    def compare_with_copic(self, copic_color: CopicColor) -> tuple[Color, float]:
        target_rgb = copic_color.as_srgb()
        color_dict_match = self.most_similar(target_rgb)

        copic_cie = colour.sRGB_to_XYZ(target_rgb)
        color_dict_cie = colour.sRGB_to_XYZ(color_dict_match.as_srgb())

        delta = colour.delta_E(copic_cie, color_dict_cie)

        return color_dict_match, float(delta)


def parse_copic_code(code: CCC) -> tuple[int, int]:
    """
    Parse a Copic color code to extract saturation and brightness values.
    Returns (saturation, brightness) as integers.

    Rules:
    - First digit after letter(s) = saturation (single digit)
    - Remaining digits = brightness (can be 1, 2, or 3 digits)
    - Black (_110): saturation=9, brightness=9
    - White (_000): saturation=0, brightness=0

    Examples:
    - R05 -> (0, 5): saturation=0, brightness=5
    - R89 -> (8, 9): saturation=8, brightness=9
    - B0000 -> (0, 0): saturation=0, brightness=0
    - W4 -> (0, 4): single digit = brightness only
    - FBG2 -> (5, 2): special color, fixed saturation=5, brightness=5
    - _110 -> (9, 9): black
    - _000 -> (0, 0): white
    """
    name = code.name

    # Handle special named colors
    if name == "_110":  # Black
        return (9, 9)
    elif name == "_000":  # White
        return (0, 0)

    # Extract digits
    digits = "".join(c for c in name if c.isdigit())

    if name.startswith("F"):
        # Flourescent color, using saturation 5, brightness 5
        return (5, 5)
    elif len(digits) == 1:
        # Single digit = brightness only (e.g., W4)
        return (0, int(digits))
    else:
        # Standard format: first digit = saturation, remaining digits = brightness
        saturation = int(digits[0])
        brightness = int(digits[1:])
        return (saturation, brightness)


def select_contrasting_colors(
    color_group: CCG | None = None,
    count: int = 2,
    contrast_param: str = "saturation",
    min_primary_contrast: int = 4,
    cross_group: bool = False,
) -> list[CopicColor]:
    """
    Select colors with high contrast from the same color group or across groups.

    Args:
        color_group: The color group to select from (e.g., CCG.R). Ignored if cross_group=True.
        count: Number of colors to select (minimum 2)
        contrast_param: "saturation" or "brightness" - the primary dimension to contrast
        min_primary_contrast: Minimum difference in the primary parameter from seed color
        cross_group: If True, select colors across all color groups (tends to prefer different groups)

    Returns:
        List of Color objects with high contrast
    """
    if count < 2:
        raise ValueError("count must be at least 2")
    if contrast_param not in ["saturation", "brightness"]:
        raise ValueError("contrast_param must be 'saturation' or 'brightness'")
    if not cross_group and color_group is None:
        raise ValueError("color_group must be specified when cross_group=False")

    copic = Copic()

    # Get color codes from appropriate source
    if cross_group:
        # Get all color codes from all groups
        all_groups = list(CCG)
        parsed_colors = []
        for group in all_groups:
            group_codes = copic.get_colors_by_group(group)
            parsed_colors.extend([(code, *parse_copic_code(code)) for code in group_codes])
    else:
        # Get color codes from single group (color_group is guaranteed non-None by validation)
        assert color_group is not None
        color_codes = copic.get_colors_by_group(color_group)
        parsed_colors = [(code, *parse_copic_code(code)) for code in color_codes]

    # Randomly select seed color
    seed_code, seed_sat, seed_bright = random.choice(parsed_colors)
    selected = [copic.color_by_code(seed_code)]
    selected_groups = {copic.color_by_code(seed_code).group}

    # Determine which dimension to use for primary contrast
    seed_value = seed_sat if contrast_param == "saturation" else seed_bright

    # Find candidates with sufficient primary contrast from seed
    candidates = [
        (code, sat, bright)
        for code, sat, bright in parsed_colors
        if abs((sat if contrast_param == "saturation" else bright) - seed_value) >= min_primary_contrast
    ]

    if not candidates:
        # If no candidates meet primary threshold, relax it
        candidates = [(code, sat, bright) for code, sat, bright in parsed_colors if code != seed_code]

    # Select remaining colors ensuring they're distributed
    while len(selected) < count and candidates:
        # Find candidate with good contrast from already-selected colors
        best_candidate = None
        best_min_contrast = -1
        best_is_new_group = False

        for candidate_code, cand_sat, cand_bright in candidates:
            # Calculate minimum contrast to all already-selected colors
            cand_value = cand_sat if contrast_param == "saturation" else cand_bright

            min_contrast = float("inf")
            for sel_color in selected:
                sel_sat, sel_bright = parse_copic_code(sel_color.code)
                sel_value = sel_sat if contrast_param == "saturation" else sel_bright
                contrast = abs(cand_value - sel_value)
                min_contrast = min(min_contrast, contrast)

            # Check if candidate is from a new group (for cross_group mode)
            candidate_color = copic.color_by_code(candidate_code)
            is_new_group = cross_group and candidate_color.group not in selected_groups

            # Prefer candidates with better minimum contrast
            # In cross_group mode, give slight preference to new groups when contrast is similar
            is_better = False
            if cross_group and is_new_group and not best_is_new_group:
                # New group is always better if we don't have one yet (and contrast is reasonable)
                is_better = min_contrast > 0
            elif cross_group and best_is_new_group and not is_new_group:
                # Already have new group candidate, this one isn't new - only better if much higher contrast
                is_better = min_contrast > best_min_contrast * 1.5
            else:
                # Normal comparison - just use contrast
                is_better = min_contrast > best_min_contrast

            if is_better:
                best_min_contrast = min_contrast
                best_candidate = candidate_code
                best_is_new_group = is_new_group

        if best_candidate:
            best_color = copic.color_by_code(best_candidate)
            selected.append(best_color)
            selected_groups.add(best_color.group)
            candidates = [(c, s, b) for c, s, b in candidates if c != best_candidate]
        else:
            break

    return selected


def select_similar_colors(
    count: int = 2,
    max_contrast: int = 3,
) -> list[CopicColor]:
    """
    Select colors with low contrast (similar colors) across all color groups.
    Colors must be similar in either saturation OR brightness (flexible matching).
    Prefers selecting from different color groups for visual variety.

    Args:
        count: Number of colors to select (minimum 2)
        max_contrast: Maximum difference allowed in saturation OR brightness (default 3)

    Returns:
        List of Color objects with low contrast

    Raises:
        ValueError: If count < 2 or if not enough similar colors can be found
    """
    if count < 2:
        raise ValueError("count must be at least 2")

    copic = Copic()

    # Get all color codes from all groups
    all_groups = list(CCG)
    parsed_colors = []
    for group in all_groups:
        group_codes = copic.get_colors_by_group(group)
        parsed_colors.extend([(code, *parse_copic_code(code)) for code in group_codes])

    # Randomly select seed color
    seed_code, seed_sat, seed_bright = random.choice(parsed_colors)
    selected = [copic.color_by_code(seed_code)]
    selected_groups = {copic.color_by_code(seed_code).group}

    # Find candidates similar to seed (low contrast in saturation OR brightness)
    candidates = [
        (code, sat, bright)
        for code, sat, bright in parsed_colors
        if code != seed_code and (abs(sat - seed_sat) <= max_contrast or abs(bright - seed_bright) <= max_contrast)
    ]

    if len(candidates) < count - 1:
        raise ValueError(
            f"Not enough similar colors found. Requested {count}, but only found "
            f"{len(candidates) + 1} colors within max_contrast={max_contrast}. "
            f"Seed: {seed_code.name} (sat={seed_sat}, bright={seed_bright})"
        )

    # Select remaining colors, preferring different groups
    while len(selected) < count and candidates:
        best_candidate = None
        best_similarity_score = float("inf")
        best_is_new_group = False

        for candidate_code, cand_sat, cand_bright in candidates:
            # Calculate similarity to all selected colors (lower is more similar)
            # Use minimum difference in either saturation or brightness
            max_diff_to_any_selected = 0
            for sel_color in selected:
                sel_sat, sel_bright = parse_copic_code(sel_color.code)
                # Take the minimum of sat or bright difference (flexible matching)
                min_diff = min(abs(cand_sat - sel_sat), abs(cand_bright - sel_bright))
                max_diff_to_any_selected = max(max_diff_to_any_selected, min_diff)

            # Check if candidate is from a new group
            candidate_color = copic.color_by_code(candidate_code)
            is_new_group = candidate_color.group not in selected_groups

            # Selection logic: prefer new groups, but maintain similarity
            is_better = False
            if is_new_group and not best_is_new_group:
                # New group is preferred if similarity is reasonable
                is_better = max_diff_to_any_selected <= max_contrast
            elif not is_new_group and best_is_new_group:
                # Already have new group candidate - only replace if significantly more similar
                is_better = max_diff_to_any_selected < best_similarity_score * 0.5
            else:
                # Both new or both not new - prefer more similar
                is_better = max_diff_to_any_selected < best_similarity_score

            if is_better:
                best_similarity_score = max_diff_to_any_selected
                best_candidate = candidate_code
                best_is_new_group = is_new_group

        if best_candidate and best_similarity_score <= max_contrast:
            best_color = copic.color_by_code(best_candidate)
            selected.append(best_color)
            selected_groups.add(best_color.group)
            candidates = [(c, s, b) for c, s, b in candidates if c != best_candidate]
        else:
            # Could not find enough similar colors
            raise ValueError(
                f"Could not find {count} similar colors within max_contrast={max_contrast}. "
                f"Only found {len(selected)} colors."
            )

    return selected
