from cursor.collection import Collection
from cursor.renderer.realtime import RealtimeRenderer, Buffer


def disabled_test_realtime():
    collection = Collection.from_tuples([[(0, 0), (300, 300)], [(0, 300), (300, 0)]])

    renderer = RealtimeRenderer(300, 300, "test")
    renderer.add_collection(collection)

    buffer = Buffer(300, 300)

    buffer.clear()
    buffer.use()
    renderer.shapes.draw()

    renderer.clear()
    renderer.use()
    buffer.draw()

    renderer.run()
