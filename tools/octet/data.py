from cursor.data import DataDirHandler
from cursor.loader import Loader
from cursor.collection import Collection
from cursor.path import Path

import random

recordings = DataDirHandler().recordings()
_loader = Loader(directory=recordings, limit_files=1)
all_paths = _loader.all_paths()

all_paths = Collection()
p = Path()
for i in range(100):
    p.add(random.randint(-10, 10), random.randint(-10, 10))
all_paths.add(p)