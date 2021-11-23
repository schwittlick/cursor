from cursor.renderer import RealtimeRenderer
from cursor.path import PathCollection
from cursor.path import Path

if __name__ == "__main__":
    pc = PathCollection()
    p1 = Path()
    p1.add(0, 0)
    p1.add(200, 0)
    p2 = Path()
    p2.add(0, 200)
    p2.add(200, 200)

    pc.add(p1)
    pc.add(p2)

    r = RealtimeRenderer()
    r.render(pc)
