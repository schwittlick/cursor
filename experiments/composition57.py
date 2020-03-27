import streamlit as st

from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

@st.cache
def load_data():
    p = data.DataHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=1)
    return ll

def composition57(nr, pathlist):
    folder = data.DataHandler().jpg("composition56")
    #gcode_renderer = renderer.GCodeRenderer("composition56", z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer(folder)
    xoffset = 0

    xspacing = 1
    coll = path.PathCollection(rec.resolution)

    for p in pathlist:
        for i in range(250):
            xfrom = xspacing * i + xoffset
            yfrom = 0
            xto = xspacing * i + xoffset
            yto = 1000
            morphed = p.morph((xfrom, yfrom), (xto, yto))
            coll.add(morphed, rec.resolution)

        xoffset += 400

    coll.fit(path.Paper.a1_landscape(), 50)

    hash = pathlist[0].hash()

    print(f"rendering {nr}, {coll.bb()}")
    #gcode_renderer.render(coll, f"composition56_{hash}")
    img = jpeg_renderer.render(coll, f"composition56_{hash}")
    st.image(img, caption='Sunrise by the mountains', use_column_width = True)

if __name__ == "__main__":
    st.title('Composition #57')
    ll = load_data()
    rec = ll.single(0)
    all_paths = ll.all_paths()

    #entropy_filter = filter.EntropyFilter(1.2, 1.2)
    #all_paths.filter(entropy_filter)

    #distance_filter = filter.DistanceFilter(100, rec.resolution)
    #all_paths.filter(distance_filter)

    for i in range(1):
        r1 = all_paths.random()
        r2 = all_paths.random()
        r3 = all_paths.random()
        r4 = all_paths.random()
        r5 = all_paths.random()

        print(r1.hash())

        composition57(i, [r1, r2, r3, r4, r5])