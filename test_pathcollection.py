import path
import pyautogui

def test_pathcollection_minmax():
    size = pyautogui.Size(100, 100)
    pcol = path.PathCollection(size)

    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(10, 11, 10001)
    p1.add(11, 11, 10002)
    p1.add(20, 20, 10003)
    p1.add(30, 31, 10004)
    p1.add(40, 41, 10005)

    p2 = path.Path()

    p2.add(545, 54, 10000)
    p2.add(160, 11, 10001)
    p2.add(11, 171, 10002)
    p2.add(20, 20, 10003)
    p2.add(30, 31, 10004)
    p2.add(940, 941, 10005)

    pcol.add(p1, size)
    pcol.add(p2, size)

    min = pcol.min()
    max = pcol.max()
    assert min[0] == 5
    assert min[1] == 11
    assert max[0] == 940
    assert max[1] == 5111