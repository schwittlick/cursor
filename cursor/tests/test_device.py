from cursor.device import DrawingMachine


def test_simple_drawing_machine():
    dm = DrawingMachine()
    assert dm.connect("ANY", 12456) is False

    dm.stream("file")
