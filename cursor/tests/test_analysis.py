from cursor.analysis import Histogram
from cursor.data import DataDirHandler
from cursor.loader import Loader


def test_simple_histogram():
    h = Histogram()

    # path direction change histogram
    # p = Path()
    # for i in range(10000):
    #    r1 = random.randint(-100, 100)
    #    r2 = random.randint(-100, 100)
    #    p.add(x=r1, y=r2)

    # h.get(p.direction_changes())

    dir = DataDirHandler().recordings()
    single_file = dir.joinpath("1565088885.39372_compressed.json")
    ll = Loader(directory=dir, limit_files=2)
    # ll.load_file(single_file)

    shannxs = []
    shannys = []
    shannchan = []
    pps = ll.all_paths()
    for p2 in pps:
        # print(p2)
        # changes = p2.direction_changes()
        shannxs.append(p2.shannon_x)
        shannys.append(p2.shannon_y)
        shannchan.append(p2.shannon_direction_changes)
        # print(changes)
        # hist, bins = h.get(changes)
        # print("1")
    #        exit(0)

    histx, binsx = h.get(shannxs)
    histy, binsy = h.get(shannys)
    histch, binsch = h.get(shannchan)
    print(histx)
    print(binsx)
    print(histy)
    print(binsy)
    print(histch)
    print(binsch)
