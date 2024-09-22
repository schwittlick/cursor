from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode


def test_rgb_data():
    assert len(Copic().available_colors) == 177


def test_singleton():
    c1 = Copic()
    c2 = Copic()

    assert c1 is c2


def test_most_similar():
    assert Copic().most_similar((0.2, 0.3, 0.4)).code is CopicColorCode.V99
    assert Copic().most_similar((0, 0, 0)).code is CopicColorCode._110
    assert Copic().most_similar((1, 1, 1)).code is CopicColorCode.B0000
    assert Copic().most_similar((0.9, 0.9, 0.9)).code is CopicColorCode.W1


def test_most_similar_srgb_kdtree():
    assert Copic().most_similar_rgb_kdtree((0.2, 0.3, 0.4)).code is CopicColorCode.V99
    assert Copic().most_similar_rgb_kdtree((0, 0, 0)).code is CopicColorCode._110
    assert Copic().most_similar_rgb_kdtree((1, 1, 1)).code is CopicColorCode.B0000
    assert Copic().most_similar_rgb_kdtree((0.9, 0.9, 0.9)).code is CopicColorCode.W1
