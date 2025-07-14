from cursor.position import Position
from cursor.renderer.realtime import RealtimeRenderer
from cursor.algorithm.color.named_colors import NamedColor


def disabled_test_realtime():
    dimension = 2000

    renderer = RealtimeRenderer(dimension, dimension, "test")
    renderer.add_point(
        Position.from_tuple((1000, 1000)), width=200, color=NamedColor.WHITE
    )

    renderer.run()
