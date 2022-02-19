from cursor.renderer import RealtimeRenderer
from cursor.path import PathCollection
from cursor.path import Path

if __name__ == "__main__":
    pc = PathCollection()
    p1 = Path()
    p1.add(10, 10)
    p1.add(200, 10)
    p2 = Path()
    p2.add(10, 200)
    p2.add(200, 200)

    pc.add(p1)
    pc.add(p2)

    r = RealtimeRenderer()
    r.render(pc)
