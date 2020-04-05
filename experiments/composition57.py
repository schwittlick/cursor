import streamlit as st
import random

from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data

p = data.DataPathHandler().recordings()
ll = loader.Loader(directory=p, limit_files=1)


def composition57(pc):
    folder = data.DataPathHandler().jpg("composition57")
    gcode_folder = data.DataPathHandler().gcode("composition57")
    jpeg_renderer = renderer.JpegRenderer(folder)
    gcode_renderer = renderer.GCodeRenderer(gcode_folder)

    xspacing = 1
    coll = path.PathCollection()
    offsets = offsets1()

    line_count = st.sidebar.number_input("Line count", 1, 200, 100)

    counter = 0
    for p in pc:
        offsets[counter] = st.sidebar.number_input(
            f"offset {p.hash()}", 0, 3000, offsets[counter]
        )
        for i in range(line_count):
            xfrom = xspacing * i + offsets[counter]
            yfrom = 0
            xto = xspacing * i + offsets[counter]
            yto = 200
            morphed = p.morph((xfrom, yfrom), (xto, yto))
            coll.add(morphed)

        if counter < 4:
            offsets[counter + 1] = offsets[counter] + line_count

        counter += 1

    coll.fit(path.Paper.a1_landscape(), 40)

    filename = f"composition57_{pc.hash()}"

    jpeg_renderer.render(coll, scale=3.0, frame=True)

    st.write(f"Image size: {jpeg_renderer.img.size}")

    if st.sidebar.checkbox("render bb"):
        jpeg_renderer.render_bb(coll.bb())

    st.image(
        jpeg_renderer.img, caption=f"Composition #57 {pc.hash()}", use_column_width=True
    )

    if st.sidebar.button("save"):
        st.write(f"Saving {filename}")
        gcode_renderer.render(coll, filename)
        jpeg_renderer.save(filename)


@st.cache(allow_output_mutation=True)
def inputs1():
    return [0, 1, 2, 3, 4]


@st.cache(allow_output_mutation=True)
def offsets1():
    return [0, 100, 200, 300, 400]


def main():
    st.title("Composition #57")
    all_paths = ll.all_paths()

    st.sidebar.markdown("EntropyFilter")
    min_slider = st.sidebar.slider("min entropy", 0.0, 10.0, 3.5)
    max_slider = st.sidebar.slider("max entropy", 0.0, 10.0, 5.0)
    entropy_filter = filter.EntropyFilter(min_slider, max_slider)
    all_p = all_paths.filtered(entropy_filter)

    st.sidebar.text(f"Before filtering: {len(all_paths)}")
    st.sidebar.text(f"After filtering: {len(all_p)}")

    inputs = inputs1()

    if st.sidebar.button("randomize 1"):
        inputs[0] = int(random.randint(0, len(all_p) - 1))
    if st.sidebar.button("randomize 2"):
        inputs[1] = int(random.randint(0, len(all_p) - 1))
    if st.sidebar.button("randomize 3"):
        inputs[2] = int(random.randint(0, len(all_p) - 1))
    if st.sidebar.button("randomize 4"):
        inputs[3] = int(random.randint(0, len(all_p) - 1))
    if st.sidebar.button("randomize 5"):
        inputs[4] = int(random.randint(0, len(all_p) - 1))

    i1 = st.sidebar.number_input("i1", 0, len(all_p), inputs[0])
    i2 = st.sidebar.number_input("i2", 0, len(all_p), inputs[1])
    i3 = st.sidebar.number_input("i3", 0, len(all_p), inputs[2])
    i4 = st.sidebar.number_input("i4", 0, len(all_p), inputs[3])
    i5 = st.sidebar.number_input("i5", 0, len(all_p), inputs[4])

    pc = path.PathCollection()
    pc.add(all_p[i1])
    pc.add(all_p[i2])
    pc.add(all_p[i3])
    pc.add(all_p[i4])
    pc.add(all_p[i5])

    composition57(pc)


if __name__ == "__main__":
    main()
