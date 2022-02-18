import os
import glob
import pathlib

if __name__ == "__main__":
    with open("julis_movie_list.txt", "w") as file:
        #for filename in glob.iglob("D:\\movies_julius_marcel\\" + '**/**', recursive=True):
        #    p = pathlib.Path(filename)
        #    print(p.as_posix())
        #

        path = pathlib.Path("D:\\movies_julius_marcel\\")
        for p in path.rglob("*"):

            print(p.as_posix())
            file.write(p.as_posix() + "\n")