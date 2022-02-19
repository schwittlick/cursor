import pathlib

if __name__ == "__main__":
    with open("julis_movie_list.txt", "w") as file:
        path = pathlib.Path("D:\\movies_julius_marcel\\")
        for p in path.rglob("*"):

            print(p.as_posix())
            file.write(p.as_posix() + "\n")
