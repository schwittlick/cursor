import pathlib
import logging

from cursor.properties import Property
from cursor.renderer import BaseRenderer

from fpdf import FPDF


class PdfRenderer(BaseRenderer):
    def __init__(self, folder: pathlib.Path):
        super().__init__(folder)

        self.margin_x = 0
        self.margin_y = 0

        self.reset()

    def reset(self, orientation: str = "Portrait", w: int = 210, h: int = 297):
        self.pdf = FPDF(orientation=orientation, unit="mm", format=(w, h))
        self.pdf.set_author("Marcel Schwittlick")
        self.pdf.set_margins(self.margin_x, self.margin_y)

    def render(self, scale: float = 1.0) -> None:
        self.render_all_paths(scale=scale)
        self.render_all_points(scale=scale)
        self.clear()

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".pdf")
        self.pdf.output(fname.as_posix())

        logging.info(f"Finished saving {fname.name}")
        logging.info(f"in {self.save_path}")

    def background(self, r: int, g: int, b: int) -> None:
        self.pdf.set_fill_color(r, g, b)
        self.pdf.rect(0, 0, self.pdf.w, self.pdf.h, "F")

    def circle(self, x: float, y: float, r: float) -> None:
        self.pdf.circle(x=x - r, y=y - r, r=r * 2, style="F")

    def render_page_nr(self, r: int, g: int, b: int) -> None:
        self.pdf.set_fill_color(r, g, b)
        self.pdf.text(self.pdf.w / 2, self.pdf.h * 0.98, str(self.pdf.page_no()))

    def render_all_paths(self, scale: float = 1.0) -> None:
        for path in self.collection:
            path.scale(scale, scale)
            r, g, b = path.properties[Property.COLOR]
            width = path.properties[Property.WIDTH]
            self.pdf.set_line_width(width)
            self.pdf.set_draw_color(r, g, b)
            self.pdf.polyline(path.as_tuple_list())

    def render_all_points(self, scale: float = 1.0) -> None:
        for point in self.positions:
            rad = point.properties[Property.RADIUS]
            r, g, b = point.properties[Property.COLOR]
            self.pdf.set_fill_color(r, g, b)
            self.pdf.circle(point.x * scale, point.y * scale, rad, "fill")
