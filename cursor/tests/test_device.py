from cursor.device import DrawingMachine

import pytest


def test_simple_drawing_machine():
    dm = DrawingMachine()
    assert dm.connect("ANY", 12456) is False

    with pytest.raises(AssertionError):
        dm.stream("file")
