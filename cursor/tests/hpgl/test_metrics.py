import pytest

from cursor.hpgl.metrics import (
    DEFAULT_CHAR_ASPECT,
    LABEL_ORIGINS,
    FontMetrics,
    label_origin_offset,
)


def test_default_metrics():
    metrics = FontMetrics.default()

    assert metrics.char_width_cm == 0.285
    assert metrics.char_height_cm == 0.375
    assert metrics.extra_space == 0.0
    assert metrics.char_width_cm / metrics.char_height_cm == DEFAULT_CHAR_ASPECT


def test_cell_is_wider_and_taller_than_the_glyph():
    metrics = FontMetrics(0.1, 0.1)

    assert metrics.advance_x == pytest.approx(metrics.char_width * 1.5)
    assert metrics.line_height == pytest.approx(metrics.char_height * 2.0)


def test_extra_space_is_a_fraction_of_the_cell():
    loose = FontMetrics(0.1, 0.1, extra_space=1.0)
    tight = FontMetrics(0.1, 0.1, extra_space=-0.5)
    plain = FontMetrics(0.1, 0.1)

    assert loose.advance_x == pytest.approx(plain.advance_x * 2)
    assert tight.advance_x == pytest.approx(plain.advance_x * 0.5)


def test_glyphs_touch_at_minus_a_third():
    metrics = FontMetrics(0.1, 0.1, extra_space=-1 / 3)

    assert metrics.advance_x == pytest.approx(metrics.char_width)


def test_label_origin_left_bottom_is_the_point_itself():
    metrics = FontMetrics(0.285, 0.375)

    assert label_origin_offset(1, 1000, metrics) == (0.0, 0.0)


def test_label_origin_shifts_back_by_the_labels_own_extent():
    metrics = FontMetrics(0.285, 0.375)
    height = metrics.char_height

    # left/centre/right by bottom/centre/top
    assert label_origin_offset(3, 1000, metrics) == (0.0, -height)
    assert label_origin_offset(5, 1000, metrics) == (-500.0, -height / 2)
    assert label_origin_offset(7, 1000, metrics) == (-1000.0, 0.0)
    assert label_origin_offset(9, 1000, metrics) == (-1000.0, -height)


def test_label_origin_clearance_pushes_away_from_the_point():
    metrics = FontMetrics(0.285, 0.375)
    half_w, half_h = metrics.char_width / 2, metrics.char_height / 2

    # 11 is 1 with clearance: the label already extends up and right, so it moves that way
    plain_x, plain_y = label_origin_offset(1, 1000, metrics)
    clear_x, clear_y = label_origin_offset(11, 1000, metrics)
    assert (clear_x - plain_x, clear_y - plain_y) == pytest.approx((half_w, half_h))

    # 19 is 9 with clearance, extending down and left
    plain_x, plain_y = label_origin_offset(9, 1000, metrics)
    clear_x, clear_y = label_origin_offset(19, 1000, metrics)
    assert (clear_x - plain_x, clear_y - plain_y) == pytest.approx((-half_w, -half_h))

    # a centred axis has no direction to clear in
    assert label_origin_offset(15, 1000, metrics) == label_origin_offset(5, 1000, metrics)


def test_label_origin_rejects_invalid():
    metrics = FontMetrics(0.285, 0.375)

    for origin in (0, 10, 20, -1):
        assert origin not in LABEL_ORIGINS
        with pytest.raises(ValueError):
            label_origin_offset(origin, 1000, metrics)
