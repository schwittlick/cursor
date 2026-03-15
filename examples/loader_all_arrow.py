from cursor.data import DataDirHandler
from cursor.load.arrow_loader import ArrowLoader

if __name__ == "__main__":
    ll = ArrowLoader(directory=DataDirHandler().recordings())
    c = ll.all_paths()
    print(f"Total paths: {len(c)}")
