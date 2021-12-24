from cursor import data
from cursor import loader

import wasabi

log = wasabi.Printer()

if __name__ == "__main__":
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=None)
    all_paths = ll.all_paths()
    log.info(f"Valid path count: {len(all_paths)}")
