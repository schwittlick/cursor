from cursor import path
from cursor import renderer


if __name__ == "__main__":
    pc1 = path.PathCollection()
    pc2 = path.PathCollection()

    p = path.Path()
    p.add(0, 0)
    p.add(1, 0)
    p.add(1, 1)
    p.add(0, 1)
    p.add(0, 0)
    p.scale(600, 600)
    pc1.add(p)

    p2 = path.Path()
    p2.add(0, 0)
    p2.add(1, 0)
    p2.add(1, 1)
    p2.add(0, 1)
    p2.add(0, 0)
    p2.scale(40, 40)
    p2.translate(200, 200)
    pc2.add(p2)

    rr = renderer.RealtimeRenderer(850, 600)
    rr.add(pc1)
    rr.add(pc2)

    rr.render()
