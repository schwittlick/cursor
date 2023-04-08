from cursor.data import DataDirHandler
from cursor.loader import Loader

recordings = DataDirHandler().recordings()
_loader = Loader(directory=recordings, limit_files=1)
all_paths = _loader.all_paths()
