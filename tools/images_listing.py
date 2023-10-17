import os
import pathlib

"""
This prints a list of files for the overview-website
"""
if __name__ == "__main__":
    folder = "C:\\Users\\schwittlick\\dev\\schwittlick.net\\img\\works\\"
    folder = pathlib.Path(folder)

    data = {}
    for x in os.walk(folder):
        elements = x[2]
        data[x[0][41:]] = elements
    del data["img\\works"]
    print(data)
