from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode as CCC
from cursor.algorithm.color.copic_pen_enum import CopicColorGroup as CCG


def test_rgb_data():
    assert len(Copic().available_colors) == 206


def test_singleton():
    c1 = Copic()
    c2 = Copic()

    assert c1 is c2


def test_most_similar():
    assert Copic().most_similar((0.2, 0.3, 0.4)).code is CCC.V99
    assert Copic().most_similar((0, 0, 0)).code is CCC._110
    assert Copic().most_similar((1, 1, 1)).code is CCC.B0000
    assert Copic().most_similar((0.9, 0.9, 0.9)).code is CCC.N1


def test_most_similar_srgb_kdtree():
    assert Copic().most_similar_rgb_kdtree((0.2, 0.3, 0.4)).code is CCC.BV29  # difference?
    assert Copic().most_similar_rgb_kdtree((0, 0, 0)).code is CCC._110
    assert Copic().most_similar_rgb_kdtree((1, 1, 1)).code is CCC.B0000
    assert Copic().most_similar_rgb_kdtree((0.9, 0.9, 0.9)).code is CCC.N1


def test_get_colors_by_group():
    copic = Copic()
    colors = copic.get_colors_by_group(CCG.R)
    assert isinstance(colors, list)
    assert len(colors) > 0
    assert all(isinstance(color, CCC) for color in colors)
    assert CCC.R00 in colors
    assert CCC.R89 in colors


def test_get_colors_by_group_all_groups():
    """
    Test the get_colors_by_group method of the Copic class.

    This function verifies that the get_colors_by_group method returns the correct
    list of colors for each color group in the CopicColorGroup (CCG) enum.

    The test checks that:
    1. The returned value is a list.
    2. The list is not empty.
    3. All items in the list are instances of CopicColorCode (CCC).
    4. The returned list matches the corresponding list in available_colors_pens.

    No parameters are required as this is a test function.

    Returns:
        None. Assertions will raise exceptions if the test fails.
    """
    copic = Copic()
    for ccg in CCG:
        colors = copic.get_colors_by_group(ccg)
        assert isinstance(colors, list)
        assert len(colors) > 0
        assert all(isinstance(color, CCC) for color in colors)
        assert colors == copic.available_colors_pens[ccg]


def test_get_colors_by_group_consistent_order():
    """
    Test the consistency of the order of colors returned by get_colors_by_group method.

    This function verifies that the get_colors_by_group method of the Copic class
    returns the same list of colors in the same order when called multiple times
    for the same color group.

    The test uses the CCG.R (Red) color group as an example and performs the following checks:
    1. The lists returned by two consecutive calls are identical.
    2. The values of the color enums in both lists are in the same order.

    Parameters:
        None

    Returns:
        None. Assertions will raise exceptions if the test fails.
    """
    copic = Copic()
    group = CCG.R  # Choose a specific color group for testing

    colors_first_call = copic.get_colors_by_group(group)
    colors_second_call = copic.get_colors_by_group(group)

    assert colors_first_call == colors_second_call
    assert [color.value for color in colors_first_call] == [color.value for color in colors_second_call]


def test_get_colors_by_group_all_enums():
    """
    Test the get_colors_by_group method for all color groups in the CopicColorGroup enum.

    This function verifies that the get_colors_by_group method of the Copic class
    returns the correct list of colors for each color group defined in the
    CopicColorGroup (CCG) enum.

    The test checks that:
    1. The returned value is a list.
    2. The list is not empty.
    3. All items in the list are instances of CopicColorCode (CCC).
    4. The returned list matches the corresponding list in available_colors_pens.

    Parameters:
        None

    Returns:
        None. Assertions will raise exceptions if the test fails.
    """
    copic = Copic()
    for ccg in CCG:
        colors = copic.get_colors_by_group(ccg)
        assert isinstance(colors, list)
        assert len(colors) > 0
        assert all(isinstance(color, CCC) for color in colors)
        assert colors == copic.available_colors_pens[ccg]
