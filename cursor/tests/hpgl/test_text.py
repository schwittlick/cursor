import pytest

from cursor.bb import BoundingBox
from cursor.hpgl import text
from cursor.hpgl.hpgl import HPGL


def test_font_metrics_defaults():
    metrics = text.FontMetrics(0.285, 0.375)

    assert metrics.char_width == pytest.approx(114.0)
    assert metrics.char_height == pytest.approx(150.0)
    assert metrics.advance_x == pytest.approx(171.0)
    assert metrics.line_height == pytest.approx(300.0)


def test_font_metrics_spacing():
    metrics = text.FontMetrics(0.285, 0.375, extra_space=1.0, extra_line=-0.5)

    assert metrics.advance_x == pytest.approx(342.0)
    assert metrics.line_height == pytest.approx(150.0)


def test_font_metrics_max_chars():
    metrics = text.FontMetrics(0.285, 0.375)

    assert metrics.max_chars(1710) == 10
    assert metrics.max_chars(0) == 0


def test_font_metrics_scaled():
    metrics = text.FontMetrics(0.285, 0.375, extra_space=0.5).scaled(2.0)

    assert metrics.char_width_cm == pytest.approx(0.57)
    assert metrics.char_height_cm == pytest.approx(0.75)
    assert metrics.extra_space == 0.5


def test_wrap_breaks_on_words():
    metrics = text.FontMetrics(0.285, 0.375)
    lines = text.wrap("aaa bbb ccc ddd", metrics, metrics.advance_x * 7)

    assert lines == ["aaa bbb", "ccc ddd"]


def test_wrap_hard_breaks_long_words():
    metrics = text.FontMetrics(0.285, 0.375)
    lines = text.wrap("aaaaaaaaa", metrics, metrics.advance_x * 4)

    assert lines == ["aaaa", "aaaa", "a"]


def test_wrap_keeps_paragraphs():
    metrics = text.FontMetrics(0.285, 0.375)
    lines = text.wrap("aaa\nbbb", metrics, metrics.advance_x * 10)

    assert lines == ["aaa", "bbb"]


def test_wrap_without_room():
    metrics = text.FontMetrics(0.285, 0.375)

    assert text.wrap("aaa", metrics, 0) == []


def test_block_dimensions():
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa", "bb"], metrics)

    assert block.width == pytest.approx(3 * metrics.advance_x)
    assert block.height == pytest.approx(2 * metrics.line_height)
    assert block.fits(BoundingBox(0, 0, 600, 600))
    assert not block.fits(BoundingBox(0, 0, 100, 600))


def test_fit_fills_the_box():
    box = BoundingBox(0, 0, 10000, 8000)
    block = text.fit("word " * 40, box)

    assert block.fits(box)
    # the width is limited by where the words happen to break, the height is not
    assert block.width > box.w * 0.8
    assert block.height > box.h * 0.9


def test_fit_shrinks_with_more_text():
    box = BoundingBox(0, 0, 10000, 8000)
    short = text.fit("word " * 10, box)
    long = text.fit("word " * 200, box)

    assert long.metrics.char_height_cm < short.metrics.char_height_cm


def test_fit_keeps_aspect_ratio():
    block = text.fit("word " * 40, BoundingBox(0, 0, 10000, 8000), char_aspect=0.5)
    metrics = block.metrics

    assert metrics.char_width_cm == pytest.approx(metrics.char_height_cm * 0.5)


def test_draw_emits_one_label_per_line():
    hpgl = HPGL()
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa", "bbb"], metrics)

    text.draw(hpgl, block, BoundingBox(0, 0, 1000, 1000))

    assert hpgl.data.count("LB") == 2
    assert f"LBaaa{chr(3)}" in hpgl.data
    assert "SI0.285,0.375;" in hpgl.data
    assert "ES0.000,0.000;" in hpgl.data
    assert "DI1.000,0.000;" in hpgl.data


def test_draw_positions_lines_from_the_top():
    hpgl = HPGL()
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa", "bbb"], metrics)

    text.draw(hpgl, block, BoundingBox(0, 0, 1000, 1000), emit_font=False)

    assert hpgl.data.startswith(f"PA0,850;LBaaa{chr(3)}PA0,550;LBbbb{chr(3)}")


def test_draw_alignment():
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa"], metrics)
    box = BoundingBox(0, 0, 1000, 1000)

    positions = {}
    for align in text.Align:
        hpgl = HPGL()
        text.draw(hpgl, block, box, align=align, emit_font=False)
        positions[align] = int(hpgl.data[2 : hpgl.data.index(",")])

    assert positions[text.Align.LEFT] == 0
    assert positions[text.Align.CENTER] == 243
    assert positions[text.Align.RIGHT] == 487


def test_draw_vertical_alignment():
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa"], metrics)
    box = BoundingBox(0, 0, 1000, 1000)

    positions = {}
    for valign in text.VAlign:
        hpgl = HPGL()
        text.draw(hpgl, block, box, valign=valign, emit_font=False)
        positions[valign] = int(hpgl.data[hpgl.data.index(",") + 1 : hpgl.data.index(";")])

    assert positions[text.VAlign.TOP] == 850
    assert positions[text.VAlign.CENTER] == 500
    assert positions[text.VAlign.BOTTOM] == 150


def test_reading_size_swaps_on_a_quarter_turn():
    box = BoundingBox(0, 0, 1000, 500)

    assert text.reading_size(box, 0) == (1000, 500)
    assert text.reading_size(box, 90) == (500, 1000)
    assert text.reading_size(box, 180) == (1000, 500)
    assert text.reading_size(box, 270) == (500, 1000)


def test_reading_size_rejects_other_angles():
    with pytest.raises(ValueError):
        text.reading_size(BoundingBox(0, 0, 1000, 500), 45)


def test_reading_box_is_anchored_at_the_origin():
    page = text.reading_box(BoundingBox(600, 600, 1600, 1100), 90)

    assert (page.x, page.y, page.w, page.h) == (0, 0, 500, 1000)


def test_fit_uses_the_turned_page():
    landscape = BoundingBox(0, 0, 10000, 8000)
    upright = text.fit("word " * 40, landscape)
    turned = text.fit("word " * 40, landscape, rotation=90)

    # the same area, but the turned block wraps to the shorter axis
    assert turned.metrics.char_height_cm < upright.metrics.char_height_cm
    assert turned.fits(text.reading_box(landscape, 90))


def test_draw_rotated_runs_along_the_other_axis():
    hpgl = HPGL()
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa", "bbb"], metrics)
    box = BoundingBox(0, 0, 1000, 1000)

    text.draw(hpgl, block, box, rotation=90, emit_font=False)

    # lines stack along +x, the baseline runs along +y
    assert hpgl.data.startswith(f"PA150,0;LBaaa{chr(3)}PA450,0;LBbbb{chr(3)}")


def test_draw_rotation_emits_direction():
    hpgl = HPGL()
    metrics = text.FontMetrics(0.285, 0.375)
    block = text.TextBlock(["aaa"], metrics)

    text.draw(hpgl, block, BoundingBox(0, 0, 1000, 1000), rotation=90)

    assert "DI0.000,1.000;" in hpgl.data


def test_draw_every_quarter_turn_stays_inside_the_box():
    metrics = text.FontMetrics(0.285, 0.375)
    box = BoundingBox(600, 600, 1600, 1600)

    for rotation in text.QUARTER_TURNS:
        hpgl = HPGL()
        block = text.layout("word " * 8, metrics, text.reading_box(box, rotation).w)
        text.draw(hpgl, block, box, rotation=rotation, emit_font=False)

        for command in hpgl.data.split(";"):
            if not command.startswith("PA"):
                continue
            x, y = (int(value) for value in command[2:].split(","))
            assert box.x <= x <= box.x2
            assert box.y <= y <= box.y2


def test_draw_chunks_long_lines():
    hpgl = HPGL()
    metrics = text.FontMetrics(0.285, 0.375)
    line = "a" * (text.MAX_LABEL_LENGTH + 10)
    block = text.TextBlock([line], metrics)

    text.draw(hpgl, block, BoundingBox(0, 0, 100000, 1000), emit_font=False)

    labels = [chunk[chunk.index("LB") + 2 :] for chunk in hpgl.data.split(chr(3))[:-1]]

    assert labels == ["a" * text.MAX_LABEL_LENGTH, "a" * 10]
