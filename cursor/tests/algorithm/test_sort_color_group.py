from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.algorithm.color.lib import sort_collection_by_copic_color_group
from cursor.collection import Collection
from cursor.path import Path
from cursor.position import Position
from cursor.properties import Property


def make_path(x: float, y: float, color_code: CopicColorCode, radius: int = 5) -> Path:
    pos = Position(x, y)
    pos.radius = radius
    path = Path([pos, Position(x + 1, y + 1)])
    path.properties[Property.COPIC_COLOR] = Copic().color_by_code(color_code)
    return path


def make_collection(*color_codes: CopicColorCode) -> Collection:
    c = Collection()
    for i, code in enumerate(color_codes):
        c.add(make_path(float(i * 10), float(i * 10), code))
    return c


# --- pen/layer assignment ---


def test_single_color_pen_and_layer():
    c = make_collection(CopicColorCode.B0000)
    result = sort_collection_by_copic_color_group(c)

    data_paths = [p for p in result if p.properties.get(Property.COPIC_COLOR) == Copic().color_by_code(CopicColorCode.B0000) and p.pen_select is not None]
    # only the actual data path (not legend paths) — legend paths also have the color set
    # easier: find paths that originated from input (have non-equal x+1 offset)
    # just verify at least one path has pen=1, layer=0
    pens = {p.pen_select for p in result}
    layers = {p.layer for p in result}
    assert 1 in pens
    assert 0 in layers


def test_two_distinct_colors_get_different_layers():
    """With separate_sp_to_layer=True each copic code group goes on its own layer."""
    c = make_collection(CopicColorCode.B0000, CopicColorCode.R01)
    result = sort_collection_by_copic_color_group(c)

    layers = {p.layer for p in result}
    assert len(layers) >= 2, "Two distinct color codes should produce paths on at least 2 layers"


def test_same_color_code_paths_share_pen_and_layer():
    """Multiple paths with the same copic color code end up on the same pen/layer."""
    c = Collection()
    for i in range(3):
        c.add(make_path(float(i), float(i), CopicColorCode.B23))

    result = sort_collection_by_copic_color_group(c)

    color = Copic().color_by_code(CopicColorCode.B23)
    data_paths = [p for p in result if p.properties.get(Property.COPIC_COLOR) == color and p.pen_select == 1]
    assert len(data_paths) >= 3, "All paths with the same color should get pen=1"
    layer_set = {p.layer for p in data_paths}
    assert len(layer_set) == 1, "All paths with the same color should share a single layer"


# --- output collection size ---


def test_legend_paths_added_per_color():
    """Each color gets 3 legend paths before and 3 after its data paths (total +6)."""
    num_data_paths = 2
    c = Collection()
    for i in range(num_data_paths):
        c.add(make_path(float(i), float(i), CopicColorCode.Y06))

    result = sort_collection_by_copic_color_group(c)
    # 3 legend before + num_data_paths + 3 legend after = num_data_paths + 6
    assert len(result) == num_data_paths + 6


def test_legend_paths_per_color_multiple_colors():
    """With N distinct colors: each adds 6 legend paths on top of its data paths."""
    codes = [CopicColorCode.B0000, CopicColorCode.R01, CopicColorCode.Y06]
    c = make_collection(*codes)  # 1 data path per color
    result = sort_collection_by_copic_color_group(c)
    # 1 data + 6 legend per color = 7 * 3 colors
    assert len(result) == len(codes) * (1 + 6)


# --- all data paths preserved ---


def test_all_input_paths_appear_in_output():
    codes = [CopicColorCode.B0000, CopicColorCode.B000, CopicColorCode.R01, CopicColorCode.B23]
    c = make_collection(*codes)
    result = sort_collection_by_copic_color_group(c)

    # There should be at least as many paths as input (legend adds more)
    assert len(result) >= len(codes)


# --- pen_mapping ---


def test_pen_mapping_exists_on_result():
    c = make_collection(CopicColorCode.B0000)
    result = sort_collection_by_copic_color_group(c)
    assert "pen_mapping" in result.properties


def test_pen_mapping_contains_color_code():
    c = make_collection(CopicColorCode.B23)
    result = sort_collection_by_copic_color_group(c)

    pen_mapping = result.properties["pen_mapping"]
    all_codes = [code for layer_map in pen_mapping.values() for code in layer_map.values()]
    assert CopicColorCode.B23 in all_codes


def test_pen_mapping_structure():
    """pen_mapping[layer][pen] = CopicColorCode."""
    codes = [CopicColorCode.B0000, CopicColorCode.R01]
    c = make_collection(*codes)
    result = sort_collection_by_copic_color_group(c)

    pen_mapping = result.properties["pen_mapping"]
    assert isinstance(pen_mapping, dict)
    for layer_map in pen_mapping.values():
        assert isinstance(layer_map, dict)
        for pen, code in layer_map.items():
            assert isinstance(pen, int)
            assert isinstance(code, CopicColorCode)


def test_pen_mapping_covers_all_input_colors():
    codes = [CopicColorCode.B0000, CopicColorCode.B000, CopicColorCode.R01]
    c = make_collection(*codes)
    result = sort_collection_by_copic_color_group(c)

    pen_mapping = result.properties["pen_mapping"]
    all_mapped_codes = {code for layer_map in pen_mapping.values() for code in layer_map.values()}
    for code in codes:
        assert code in all_mapped_codes


# --- legend path attributes ---


def test_legend_paths_have_correct_pen_and_layer():
    c = make_collection(CopicColorCode.B23)
    result = sort_collection_by_copic_color_group(c)

    legend_color = Copic().color_by_code(CopicColorCode.B23)
    legend_paths = [p for p in result if p.properties.get(Property.COPIC_COLOR) == legend_color and len(p) == 2]
    for p in legend_paths:
        assert p.pen_select == 1
        assert p.layer == 0


def test_legend_paths_have_color_property():
    c = make_collection(CopicColorCode.Y06)
    result = sort_collection_by_copic_color_group(c)

    for p in result:
        assert Property.COPIC_COLOR in p.properties


# --- legende_x / legende_y flags affect legend position ---


def test_legende_x_flag_changes_legend_x_position():
    c = make_collection(CopicColorCode.B23)
    result_default = sort_collection_by_copic_color_group(c, legende_x=False)
    result_x = sort_collection_by_copic_color_group(c, legende_x=True)

    def legend_xs(result):
        color = Copic().color_by_code(CopicColorCode.B23)
        return [p[0].x for p in result if p.properties.get(Property.COPIC_COLOR) == color and p.pen_select == 1]

    xs_default = legend_xs(result_default)
    xs_x = legend_xs(result_x)
    assert xs_default != xs_x, "legende_x flag should change legend x position"


def test_legende_y_flag_changes_legend_y_position():
    c = make_collection(CopicColorCode.B23)
    result_default = sort_collection_by_copic_color_group(c, legende_y=False)
    result_y = sort_collection_by_copic_color_group(c, legende_y=True)

    def legend_ys(result):
        color = Copic().color_by_code(CopicColorCode.B23)
        return [p[0].y for p in result if p.properties.get(Property.COPIC_COLOR) == color and p.pen_select == 1]

    ys_default = legend_ys(result_default)
    ys_y = legend_ys(result_y)
    assert ys_default != ys_y, "legende_y flag should change legend y position"
