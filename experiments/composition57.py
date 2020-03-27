import streamlit as st

from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

@st.cache
def load_data():
    p = data.DataHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=None)
    return ll

def composition57(pathlist):
    folder = data.DataHandler().jpg("composition56")
    #gcode_renderer = renderer.GCodeRenderer("composition56", z_down=3.0)
    jpeg_renderer = renderer.JpegRenderer(folder)
    xoffset = 0

    xspacing = 1
    coll = path.PathCollection(rec.resolution)

    for p in pathlist:
        for i in range(50):
            xfrom = xspacing * i + xoffset
            yfrom = 0
            xto = xspacing * i + xoffset
            yto = 1000
            morphed = p.morph((xfrom, yfrom), (xto, yto))
            coll.add(morphed, rec.resolution)

        xoffset += 400

    coll.fit(path.Paper.custom_36_48_landscape(), 50)

    hash = pathlist[0].hash()

    print(f"rendering {coll.bb()}")
    #gcode_renderer.render(coll, f"composition56_{hash}")
    img = jpeg_renderer.render(coll, f"composition56_{hash}")
    st.image(img, caption=f'Composition #57 {hash}', use_column_width = True)

if __name__ == "__main__":
    st.title('Composition #57')
    ll = load_data()
    rec = ll.single(0)
    all_paths = ll.all_paths()

    min_slider = st.slider('min entropy', 0, 10, 0)
    max_slider = st.slider('max entropy', 0, 10, 10)
    entropy_filter = filter.EntropyFilter(min_slider, max_slider)
    all_p = all_paths.filtered(entropy_filter)

    st.write(len(all_p))

    #distance_filter = filter.DistanceFilter(100, rec.resolution)
    #all_paths.filter(distance_filter)

    r1 = all_p[st.number_input('first', 0, len(all_p), 0)]
    r2 = all_p[st.number_input('first', 0, len(all_p), 1)]
    r3 = all_p[st.number_input('first', 0, len(all_p), 2)]
    r4 = all_p[st.number_input('first', 0, len(all_p), 3)]
    r5 = all_p[st.number_input('first', 0, len(all_p), 4)]

    print(r1.hash())

    composition57([r1, r2, r3, r4, r5])