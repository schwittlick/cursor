from cursor.load.loader import Loader
from cursor.data import DataDirHandler

import logging

if __name__ == "__main__":
    p = DataDirHandler().recordings()
    ll = Loader(directory=p, limit_files=None)
    all_paths = ll.all_paths()
    logging.info(f"Valid path count: {len(all_paths)}")
