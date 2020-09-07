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
    gcode_renderer = renderer.GCodeRenderer(gcode_dir, z_down=4.5)
    jpeg_renderer = renderer.JpegRenderer(jpg_dir)
    svg_renderer = renderer.SvgRenderer(svg_dir)

    pc = PathCollection()

    p = Path()
    p.add(0, 0)
    p.add(1, 1)

    pc.add(p)

    pc.fit(size=device.AxiDraw.Paper.custom_36_48_landscape(), machine=device.AxiDraw(), padding_mm=64)

    gcode_renderer.render(pc)
    jpeg_renderer.render(pc)
    svg_renderer.render(pc)

    print(pc.bb())

    jpeg_renderer.render_bb(pc.bb())
    gcode_renderer.render_bb(pc.bb())
    svg_renderer.render_bb(pc.bb())

    st.image(jpeg_renderer.img, caption=f"Sample {pc.hash()}", use_column_width=True)
    if st.sidebar.button("save"):
        gcode_renderer.save(f"straight_lines_{pc.hash()}")
        jpeg_renderer.save(f"straight_lines_{pc.hash()}")
        svg_renderer.save(f"straight_lines_{pc.hash()}")


if __name__ == "__main__":
    main()
