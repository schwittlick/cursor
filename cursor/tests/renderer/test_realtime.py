from cursor.collection import Collection
from cursor.renderer.realtime import RealtimeRenderer, Buffer


def test_realtime():
    dimension = 8000
    collection = Collection.from_tuples([[(0, 0), (dimension, dimension)], [(0, dimension), (dimension, 0)]])

    renderer = RealtimeRenderer(dimension, dimension, "test")
    renderer.add_collection(collection)

    buffer = Buffer(dimension, dimension)

    buffer.clear()
    buffer.use()
    renderer.shapes.draw()

    renderer.clear()
    renderer.use()
    buffer.draw()

    renderer.run()
