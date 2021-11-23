import streamlit as st
import random

from cursor import loader
from cursor import renderer
from cursor import path
from cursor import filter
from cursor import data
from cursor import device


@st.cache(allow_output_mutation=True)
def inputs1():
    return [0, 1, 2, 3, 4]


@st.cache(allow_output_mutation=True)
def offsets1():
    return [0, 100, 200, 300, 400]


@st.cache(
    hash_funcs={
        loader.Loader: lambda _: None,
        path.PathCollection: lambda _: None,
        path.Path: lambda _: None,
    }
)
def load_data():
    p = data.DataDirHandler().recordings()
    ll = loader.Loader(directory=p, limit_files=None)
    return ll.all_paths()


@st.cache(
    hash_funcs={
        loader.Loader: lambda _: None,
        path.PathCollection: lambda _: None,
        path.Path: lambda _: None,
        filter.EntropyMinFilter: lambda _: None,
    }
)
def apply_filter(all_paths, _min, _max):
    entropy_min_filter = filter.EntropyMinFilter(_min, _min)
    entropy_max_filter = filter.EntropyMaxFilter(_max, _max)
    r = all_paths.filtered(entropy_min_filter)
    return r.filtered(entropy_max_filter)


def composition57(pc):
    folder = data.DataDirHandler().jpg("composition57")
    jpeg_renderer = renderer.JpegRenderer(folder)

    xspacing = 1
    coll = path.PathCollection()
    offsets = offsets1()

    line_count = st.sidebar.number_input("Line count", 1, 200, 100)

    counter = 0
    for p in pc:
        offsets[counter] = st.sidebar.number_input(
            f"offset {p.hash}", 0, 3000, offsets[counter]
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

    coll.fit(device.Paper.sizes[device.PaperSize.LANDSCAPE_A1], padding_mm=100)

    filename = f"composition57_{pc.hash()}"

    jpeg_renderer.render(coll, scale=1.0, frame=True)

    st.write(f"Image size: {jpeg_renderer.img.size}")

    if st.sidebar.checkbox("render bb"):
        jpeg_renderer.render_bb(coll.bb())

    st.image(
        jpeg_renderer.img, caption=f"Composition #57 {pc.hash()}", use_column_width=True
    )

    if st.sidebar.button("save"):
        device.SimpleExportWrapper().ex(
            coll,
            device.PlotterType.DIY_PLOTTER,
            device.PaperSize.LANDSCAPE_A1,
            90,
            "composition57",
            pc.hash(),
        )

        device.SimpleExportWrapper().ex(
            coll,
            device.PlotterType.ROLAND_DPX3300,
            device.PaperSize.LANDSCAPE_A1,
            90,
            "composition57",
            pc.hash(),
        )

        st.write(f"Saving {filename}")


def main():
    st.title("Composition #57")
    all_paths = load_data()

    st.sidebar.markdown("EntropyMinFilter")
    min_slider = st.sidebar.slider("min entropy", 0.0, 10.0, 3.5)
    max_slider = st.sidebar.slider("max entropy", 0.0, 10.0, 5.0)
    all_p = apply_filter(all_paths, min_slider, max_slider)

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
