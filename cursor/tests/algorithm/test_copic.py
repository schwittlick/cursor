from cursor.algorithm.color.copic import Copic


def test_rgb_data():
    assert len(Copic().available_colors) == 72
