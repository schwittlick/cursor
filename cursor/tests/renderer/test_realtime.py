import arcade
from arcade.experimental import postprocessing

from cursor.collection import Collection
from cursor.position import Position
from cursor.renderer.realtime import RealtimeRenderer, Buffer


def disabled_test_realtime():
    dimension = 2000

    renderer = RealtimeRenderer(dimension, dimension, "test")
    renderer.add_point(
        Position.from_tuple((1000, 1000)), width=200, color=arcade.color.WHITE
    )

    renderer.run()
