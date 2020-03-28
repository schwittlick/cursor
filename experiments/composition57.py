import streamlit as st
from timeit import default_timer as timer
import pandas as pd
import time

from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

p = data.DataHandler().recordings()
ll = loader.Loader(directory=p, limit_files=1)


def composition57(pc):
    folder = data.DataHandler().jpg("composition56")
    jpeg_renderer = renderer.JpegRenderer(folder)
    xoffset = 0

    xspacing = 1
    coll = path.PathCollection()

    for p in pc:
        for i in range(50):
            xfrom = xspacing * i + xoffset
            yfrom = 0
            xto = xspacing * i + xoffset
            yto = 100
            morphed = p.morph((xfrom, yfrom), (xto, yto))
            coll.add(morphed)

        xoffset += 400

    coll.fit(path.Paper.custom_36_48_landscape(), 50)

    print(f"rendering {coll.bb()}")
    t0 = time.time()
    img = jpeg_renderer.render(coll, f"composition56_{pc.hash()}")
    t1 = time.time() - t0
    st.write(f"rendering took: {t1}s")
    st.image(img, caption=f"Composition #57 {pc.hash()}", use_column_width=True)


def main():
    # st.title('Composition #57')
    all_paths = ll.all_paths()

    st.sidebar.markdown("EntropyFilter")
    min_slider = st.sidebar.slider("min entropy", 0.0, 10.0, 3.5)
    max_slider = st.sidebar.slider("max entropy", 0.0, 10.0, 5.0)
    entropy_filter = filter.EntropyFilter(min_slider, max_slider)
    all_p = all_paths.filtered(entropy_filter)

    pc = path.PathCollection()
    for i in range(6):
        pc.add(all_p.random())

    if st.sidebar.button("random"):
        for i in range(6):
            pc.add(all_p.random())

    composition57(pc)


if __name__ == "__main__":
    main()
