from cursor import renderer
from cursor.path import PathCollection
from cursor.path import Path
from cursor import device
from cursor.data import DataDirHandler

import streamlit as st


def main():
    st.title("Simple Testing")
    gcode_dir = DataDirHandler().gcode("simple_square_test")
    jpg_dir = DataDirHandler().jpg("simple_square_test")
    svg_dir = DataDirHandler().svg("simple_square_test")
    hpgl_dir = DataDirHandler().hpgl("simple_square_test")
    gcode_renderer = renderer.GCodeRenderer(gcode_dir, z_down=4.5)
    jpeg_renderer = renderer.JpegRenderer(jpg_dir)
    svg_renderer = renderer.SvgRenderer(svg_dir)
    hpgl_renderer = renderer.HPGLRenderer(hpgl_dir)

    pc = PathCollection()

    p1 = Path()
    p1.add(-10000, -10000)
    p1.add(10000, -10000)
    p2 = Path()
    p2.add(10000, -10000)
    p2.add(10000, 10000)

    p3 = Path()
    p3.add(10000, 10000)
    p3.add(-10000, 10000)

    p4 = Path()
    p4.add(-10000, 10000)
    p4.add(-10000, -10000)

    pc.add(p1)
    pc.add(p2)
    pc.add(p3)
    pc.add(p4)

    # pc.fit(
    #    size=device.AxiDraw.Paper.custom_36_48_landscape(),
    #    machine=device.AxiDraw(),
    #    padding_mm=64,
    # )

    pc.fit(
        size=device.RolandDPX3300.Paper.a1_landscape(),
        machine=device.RolandDPX3300(),
        padding_mm=100,
        center_point=(-880, 600),
    )

    gcode_renderer.render(pc)
    # jpeg_renderer.render(pc)
    svg_renderer.render(pc)
    hpgl_renderer.render(pc)

    print(pc.bb())

    # jpeg_renderer.render_bb(pc.bb())
    gcode_renderer.render_bb(pc.bb())
    svg_renderer.render_bb(pc.bb())

    # st.image(jpeg_renderer.img, caption=f"Sample {pc.hash()}", use_column_width=True)
    if st.sidebar.button("save"):
        gcode_renderer.save(f"straight_lines_{pc.hash()}")
        # jpeg_renderer.save(f"straight_lines_{pc.hash()}")
        svg_renderer.save(f"straight_lines_{pc.hash()}")
        hpgl_renderer.save(f"straight_lines_{pc.hash()}")


if __name__ == "__main__":
    main()
