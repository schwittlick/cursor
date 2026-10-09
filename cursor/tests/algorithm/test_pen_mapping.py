from cursor.algorithm.color.copic import Color, Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.algorithm.color.lib import collapse_to_single_pen, pen_mapping_of
from cursor.collection import Collection
from cursor.path import Path
from cursor.properties import Property


def path_on(layer: str, pen: int, color: tuple[int, int, int] | None = None) -> Path:
    p = Path()
    p.add(0, 0)
    p.add(1, 1)
    p.layer = layer
    p.pen_select = pen
    if color is not None:
        p.properties[Property.COLOR] = color
    return p


def test_maps_each_layer_to_its_pens():
    c = Collection()
    c.add(path_on("fills", 2, (255, 0, 0)))
    c.add(path_on("fills", 3, (0, 255, 0)))
    c.add(path_on("lines", 1, (0, 0, 0)))

    mapping = pen_mapping_of(c)

    assert sorted(mapping) == ["fills", "lines"]
    assert sorted(mapping["fills"]) == [2, 3]
    assert mapping["fills"][2].as_rgb() == (255, 0, 0)
    assert mapping["lines"][1].as_rgb() == (0, 0, 0)


def test_many_paths_on_one_pen_collapse_to_one_entry():
    c = Collection()
    for _ in range(50):
        c.add(path_on("fills", 2, (10, 20, 30)))

    assert pen_mapping_of(c) == {"fills": {2: Color((10 / 255, 20 / 255, 30 / 255))}}


def test_prefers_a_copic_pen_over_a_plain_rgb():
    copic = Copic().color_by_code(CopicColorCode.R20)
    p = path_on("fills", 2, (1, 2, 3))
    p.properties[Property.COPIC_COLOR] = copic

    c = Collection()
    c.add(p)

    assert pen_mapping_of(c)["fills"][2] is copic


def test_conflicting_colours_on_one_pen_keep_the_first_and_warn(caplog):
    c = Collection()
    c.add(path_on("fills", 2, (255, 0, 0)))
    c.add(path_on("fills", 2, (0, 0, 255)))

    mapping = pen_mapping_of(c)

    assert mapping["fills"][2].as_rgb() == (255, 0, 0)
    assert "two colours" in caplog.text


def test_paths_without_a_colour_default_to_black():
    c = Collection()
    c.add(path_on("lines", 1))

    assert pen_mapping_of(c)["lines"][1].as_rgb() == (0, 0, 0)


def test_empty_collection_maps_to_nothing():
    assert pen_mapping_of(Collection()) == {}


def test_collapse_points_every_path_at_one_pen():
    c = Collection()
    c.add(path_on("fills", 2, (255, 0, 0)))
    c.add(path_on("fills", 3, (0, 255, 0)))
    c.add(path_on("lines", 7, (0, 0, 0)))

    collapse_to_single_pen(c)

    assert {p.pen_select for p in c} == {1}


def test_collapse_takes_a_slot_other_than_one():
    c = Collection()
    c.add(path_on("fills", 2, (255, 0, 0)))

    collapse_to_single_pen(c, pen=5)

    assert {p.pen_select for p in c} == {5}


def test_collapse_leaves_one_legend_entry_per_layer():
    c = Collection()
    for _ in range(20):
        c.add(path_on("fill_small", 2, (255, 0, 0)))
    for _ in range(20):
        c.add(path_on("fill_large", 3, (0, 0, 255)))
    c.add(path_on("lines", 4, (0, 0, 0)))

    collapse_to_single_pen(c)
    mapping = pen_mapping_of(c)

    # every layer now names the one pen to load for its file, and its colour
    assert sorted(mapping) == ["fill_large", "fill_small", "lines"]
    assert all(list(pens) == [1] for pens in mapping.values())
    assert mapping["fill_small"][1].as_rgb() == (255, 0, 0)
    assert mapping["fill_large"][1].as_rgb() == (0, 0, 255)


def test_collapse_warns_when_a_layer_loses_a_distinction(caplog):
    c = Collection()
    c.add(path_on("mixed", 2, (255, 0, 0)))
    c.add(path_on("mixed", 3, (0, 0, 255)))

    collapse_to_single_pen(c)

    assert "drew with pens [2, 3]" in caplog.text


def test_collapse_is_quiet_when_each_layer_already_had_one_pen(caplog):
    c = Collection()
    c.add(path_on("fills", 2, (255, 0, 0)))
    c.add(path_on("lines", 3, (0, 0, 0)))

    collapse_to_single_pen(c)

    assert "drew with pens" not in caplog.text


def test_mapping_is_what_the_pdf_legend_expects():
    c = Collection()
    c.add(path_on("fills", 2, (255, 0, 0)))

    for layer, pens in pen_mapping_of(c).items():
        assert isinstance(layer, str)
        for pen, color in pens.items():
            assert isinstance(pen, int)
            assert len(color.as_rgb()) == 3
