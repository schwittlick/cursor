from cursor.path import Path
from cursor.position import Position
from cursor.collection import Collection
from cursor.bb import BoundingBox


def test_bb_center():
    bb = BoundingBox(100, 200, 300, 400)
    cx, cy = bb.center()
    assert cx == 200
    assert cy == 300


def test_bb_center2():
    bb = BoundingBox(-100, -100, 100, 100)
    cx, cy = bb.center()
    assert cx == 0
    assert cy == 0


def test_bb_center3():
    bb = BoundingBox(0, 0, 300, 300)
    cx, cy = bb.center()
    assert cx == 150
    assert cy == 150


def test_bb_scale():
    bb = BoundingBox(0, 0, 100, 100)
    bb.scale(0.5)

    assert bb.x == 25
    assert bb.y == 25
    assert bb.x2 == 75
    assert bb.y2 == 75
    assert bb.w == 50
    assert bb.h == 50


def test_bb_subdiv():
    bb = BoundingBox(0, 0, 300, 300)
    subdivided = bb.subdiv(10, 10)

    assert len(subdivided) == 100

    for _bb in subdivided:
        assert _bb.w == 30
        assert _bb.h == 30


def test_inside_pos():
    bb = BoundingBox(0, 0, 300, 300)
    pos1 = Position(10, 10)
    pos2 = Position(10, 301)
    assert pos1.inside(bb)
    assert not pos2.inside(bb)

    pa = Path()
    pa.add(0, 300)
    pa.add(300, 280)

    assert pa.inside(bb)

    pa.add(-10, 10)
    assert not pa.inside(bb)

    pc = Collection()
    pc.add(pa)
    assert not pc.inside(bb)

    pc2 = Collection()
    p1 = Path()
    p1.add(100, 100)
    p1.add(100, 200)

    p2 = Path()
    p2.add(0, 0)
    p2.add(300, 300)
    pc2.add(p1)
    pc2.add(p2)

    assert pc2.inside(bb)


def test_paths_from_bb():
    bb = BoundingBox(0, 0, 300, 300)
    paths = bb.paths()

    assert len(paths) == 4
    assert paths[0] == (0, 0, 300, 0)
    assert paths[1] == (300, 0, 300, 300)
    assert paths[2] == (300, 300, 0, 300)
    assert paths[3] == (0, 300, 0, 0)
