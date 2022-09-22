from cursor.loader import Loader
from cursor.data import DataDirHandler

import linecache
import os
import tracemalloc

import cProfile
import pstats
import io
from pstats import SortKey


def display_top(snapshot, key_type="lineno", limit=10):
    snapshot = snapshot.filter_traces(
        (
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        )
    )
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        # replace "/path/to/module/file.py" with "module/file.py"
        filename = os.sep.join(frame.filename.split(os.sep)[-2:])
        print(
            "#%s: %s:%s: %.1f KiB" % (index, filename, frame.lineno, stat.size / 1024)
        )
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print("    %s" % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


def load():
    dir = DataDirHandler().recordings()
    ll = Loader(directory=dir, limit_files=1)

    rec = ll.all_paths()
    sum = 0
    for pa in rec:
        sum += len(pa)

    print(f"all point count: {sum}")


if __name__ == "__main__":
    cpf = False

    if cpf:
        pr = cProfile.Profile()
        pr.enable()

        load()

        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    tracemalloc.start()

    load()

    snapshot = tracemalloc.take_snapshot()
    display_top(snapshot)
