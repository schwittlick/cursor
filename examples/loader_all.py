from cursor.data import DataDirHandler
from cursor.load.loader import Loader

if __name__ == "__main__":
    ll = Loader(directory=DataDirHandler().recordings())
    c = ll.all_paths()
    print(f"Total paths: {len(c)}")
