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
    gcode_renderer = renderer.GCodeRenderer(gcode_dir, z_down=4.0)
    jpeg_renderer = renderer.JpegRenderer(jpg_dir)

    pc = PathCollection()

    p = Path()
    p.add(0, 0)
    p.add(1, 1)

    pc.add(p)

    pc.fit(device.DrawingMachine.Paper.CUSTOM_48_36, 50)

    gcode_renderer.render(pc)
    jpeg_renderer.render(pc)

    jpeg_renderer.render_bb(pc.bb())
    gcode_renderer.render_bb(pc.bb())

    st.image(jpeg_renderer.img, caption=f"Sample {pc.hash()}", use_column_width=True)
    if st.sidebar.button("save"):
        gcode_renderer.save(f"straight_lines_{pc.hash()}")
        jpeg_renderer.save(f"straight_lines_{pc.hash()}")


if __name__ == "__main__":
    main()
