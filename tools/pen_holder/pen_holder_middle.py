from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.hpgl.parser import stick_font
from cursor.path import Path
from cursor.properties import Property
from cursor.renderer.pdf import PdfRenderer

B = [["B0000", "B000", "B00", "B01", "B02", "B04"],
     ["B05", "B06", "B12", "B14", "B16", "B18"],
     ["B21", "B23", "B24", "B26", "B28", "B29"],
     ["B32", "B34", "B37", "B39", "B41", "B45"],
     ["B52", "B60", "B63", "B66", "B69", "B79"],
     ["B91", "B93", "B95", "B97", "B99", ""]]


def place_label(label: str) -> Collection:
    label_paths = Collection()
    for char_idx, char in enumerate(label):
        chr_paths = stick_font[char]
        for pts in chr_paths:
            path = Path.from_tuple_list(pts)
            path.properties[Property.WIDTH] = 0.1
            path.translate(char_idx * 8, 0)
            path.scale(1, -1)
            label_paths.add(path)

    return label_paths


if __name__ == "__main__":
    w = 6
    h = 6
    distance_holes = 25
    radius_holes = 5.8
    padding_holes = (distance_holes - 2 * radius_holes)

    pdf_w = w * distance_holes + padding_holes
    pdf_h = h * distance_holes + padding_holes

    pdf_dir = DataDirHandler().pdf("pen_holder")
    pdf_renderer = PdfRenderer(pdf_dir)
    pdf_renderer.reset("P", int(pdf_w), int(pdf_h))
    pdf_renderer.pdf.add_page()

    for y in range(6):
        for x in range(6):
            top = x * distance_holes + radius_holes + padding_holes
            left = y * distance_holes + radius_holes + padding_holes
            pdf_renderer.pdf.set_line_width(0.3)
            pdf_renderer.pdf.set_draw_color(255, 0, 0)
            pdf_renderer.circle(x=left, y=top, r=radius_holes)

            label = B[y][x]
            label_paths = place_label(label)

            label_x = x * distance_holes + padding_holes
            label_y = y * distance_holes

            label_paths.transform(
                BoundingBox(label_x, label_y,
                            label_x + radius_holes * 2, label_y + radius_holes * 2))
            pdf_renderer.add(label_paths)

    pdf_renderer.render()
    pdf_renderer.save("middle")
