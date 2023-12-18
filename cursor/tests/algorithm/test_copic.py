from cursor.algorithm.color.copic import Copic


def test_rgb_data():
    copic = Copic()
    assert len(copic.colors) == 126
