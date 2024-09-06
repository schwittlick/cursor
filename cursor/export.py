import random
import string
import logging
import inspect
import hashlib
import pathlib
from typing import Optional, Dict

from bb import BoundingBox
from cursor.algorithm.color.copic import Copic
from cursor.algorithm.color.copic_pen_enum import CopicColorCode
from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import (
    PlotterType,
    PlotterName,
    MinmaxMapping,
    XYFactors,
    ExportFormatMappings,
    ExportFormat,
)

from cursor.renderer.digi import DigiplotRenderer
from cursor.renderer.gcode import GCodeRenderer
from cursor.renderer.hpgl import HPGLRenderer
from cursor.renderer.jpg import JpegRenderer
from cursor.renderer.pdf import PdfRenderer
from cursor.renderer.svg import SvgRenderer
from cursor.renderer.tektronix import TektronixRenderer
from cursor.timer import Timer


class ExportConfig:
    def __init__(
            self,
            type: Optional[PlotterType] = None,
            margin: Optional[int] = None,
            cutoff: Optional[int] = None,
            export_source: bool = False,
            export_jpeg_preview: bool = False,
            optimize_hpgl_by_tsp: bool = True,
    ):
        self.type: PlotterType = type
        self.margin = margin
        self.cutoff = cutoff
        self.export_source = export_source
        self.export_jpg_preview = export_jpeg_preview
        self.optimize_hpgl_by_tsp = optimize_hpgl_by_tsp


class ExportWrapper:
    def __init__(
            self,
            paths: Collection,
            ptype: PlotterType,
            margin: int,
            name: str = "output_name",
            suffix: str = "",
            cutoff: Optional[int] = None,
            gcode_speed: Optional[int] = None,
            export_reversed: bool = False,
            keep_aspect_ratio: bool = False,
            export_jpg_preview: bool = False,
            optimize: bool = False,
    ):
        self.paths = paths
        self.ptype = ptype
        self.margin = margin
        self.name = name
        self.suffix = suffix
        self.cutoff = cutoff
        self.gcode_speed = gcode_speed
        self.export_reversed = export_reversed
        self.keep_aspect_ratio = keep_aspect_ratio

        self.config = ExportConfig(
            ptype, margin, cutoff, False, export_jpg_preview, optimize
        )

        self.exp = Exporter(paths)
        self.exp.cfg = self.config
        self.exp.name = name
        self.exp.suffix = str(suffix)
        self.exp.gcode_speed = gcode_speed
        self.exp.keep_aspect_ratio = keep_aspect_ratio

    def fit(self):
        timer = Timer()
        self.exp.fit()
        timer.print_elapsed("ExportWrapper: fit()")

    def ex(self):
        timer = Timer()
        self.exp.run()
        if self.export_reversed:
            self.exp.collection.reverse()
            self.exp.suffix = self.exp.suffix + "_reversed_"
            self.exp.run()
        timer.print_elapsed("ExportWrapper: ex()")


class Exporter:
    def __init__(self, collection: Collection):
        self.collection = collection
        self.cfg: Optional[ExportConfig] = None
        self.name: Optional[str] = None
        self.suffix: Optional[str] = None
        self.gcode_speed: Optional[int] = None
        self.keep_aspect_ratio: Optional[bool] = None

    def fit(self) -> None:
        if not self.cfg or not self.cfg.type:
            raise ValueError("Configuration or plotter type is not set")

        self.collection.fit(
            output_bounds=MinmaxMapping.maps[self.cfg.type],
            xy_factor=XYFactors.fac[self.cfg.type],
            padding_mm=self.cfg.margin,
            cutoff_mm=self.cfg.cutoff,
            keep_aspect=self.keep_aspect_ratio,
        )

    def print_pen_move_distances(self, collection: Collection):
        if not self.cfg or not self.cfg.type:
            raise ValueError("Configuration or plotter type is not set")

        unit_to_mm_factor = XYFactors.fac[self.cfg.type][0]
        pen_down_distance_mm = int(collection.calc_pen_down_distance(unit_to_mm_factor))
        pen_up_distance_mm = int(collection.calc_pen_up_distance(unit_to_mm_factor))

        logging.info(f"Total pen-down distance: {pen_down_distance_mm / 1000}meters")
        logging.info(f"Total pen-up distance: {pen_up_distance_mm / 1000}meters")

    @staticmethod
    def _file_content_of_caller():
        """
        The content of the source code of the calling file (a e.g. composition)
        is hashed and used to distinguish files later on. this is used as a unique identifier

        """
        stack = inspect.stack()
        module = inspect.getmodule(stack[3][0])
        if module:
            ms = inspect.getsource(module)
        else:
            # this is being called from a ipython notebook
            # generating a random string to be hashed below.
            # this is very hacky :(
            ms = "".join(random.choice(string.ascii_lowercase) for i in range(10))
        return ms

    def _generate_filename(self, layer: str = "") -> str:
        if not self.cfg or not self.cfg.type or not self.name or not self.suffix:
            raise ValueError("Configuration, name, or suffix is not set")

        ms = self._file_content_of_caller()
        machinename = PlotterName.names[self.cfg.type]
        h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
        hash_short = f"{h[:4]}{h[-4:]}"
        return f"{self.name}_{self.suffix}_{machinename}_{layer}_{hash_short}"

    def export_jpeg_preview(self, separate_layers: Dict[str, Collection]) -> None:
        for layer, pc in separate_layers.items():
            fname = self._generate_filename(layer)
            jpeg_folder = DataDirHandler().jpg(self.name)
            bb = self.collection.bb()
            bb.scale(0.1)
            transformed = pc.transformed(BoundingBox(0, 0, bb.w, bb.h))
            jpeg_renderer = JpegRenderer(jpeg_folder, w=int(bb.w), h=int(bb.h))
            jpeg_renderer.background((255, 255, 255))
            jpeg_renderer.add(transformed)
            jpeg_renderer.render()
            jpeg_renderer.save(fname)

    def export_source(self) -> None:
        source_folder = DataDirHandler().source(self.name)
        fname = self._generate_filename() + ".py"
        pathlib.Path(source_folder).mkdir(parents=True, exist_ok=True)
        with open(source_folder / fname, "w") as file:
            file.write(self._file_content_of_caller())
        logging.info(f"Saved source to {source_folder / fname}")

    def export_copic_color_mapping(
            self, fname: str, layers: Dict[str, Collection]
    ) -> None:
        if not self.cfg or not self.cfg.type:
            raise ValueError("Configuration or plotter type is not set")

        pdf_dir = DataDirHandler().pdf(self.name)
        pdf_renderer = PdfRenderer(pdf_dir)
        pdf_renderer.pdf.add_page()
        pdf_renderer.pdf.set_font("Arial", size=10)
        y, x = 10, 10
        layer_counter = 0

        copic = Copic()

        for layer, pc in layers.items():
            if ExportFormatMappings.maps[self.cfg.type] is ExportFormat.HPGL:
                pdf_renderer.pdf.set_fill_color(0, 0, 0)
                pdf_renderer.pdf.text(x, y, f"layer {layer}")
                y += 5
                if (
                        "pen_mapping" in self.collection.properties
                        and layer in self.collection.properties["pen_mapping"]
                ):
                    pen_mapping = self.collection.properties["pen_mapping"][layer]
                    for pen_idx, color_code in pen_mapping.items():
                        try:
                            # Convert string color code to CopicColorCode enum
                            copic_color_code = CopicColorCode[color_code]
                            c = copic.color_by_code(copic_color_code)
                            pdf_renderer.pdf.set_fill_color(0, 0, 0)
                            pdf_renderer.pdf.text(x, y, f"Pen {pen_idx} -> {c}")

                            pdf_renderer.pdf.set_fill_color(
                                c.as_rgb()[0], c.as_rgb()[1], c.as_rgb()[2]
                            )
                            pdf_renderer.circle(x + 60, y - 1, 2)
                            y += 5
                        except KeyError:
                            logging.warning(f"Invalid color code: {color_code}")
                            continue

            layer_counter += 1
            if layer_counter % 6 == 0:
                x += 65
                y = 10
        pdf_renderer.save(fname)

    def run(self) -> None:
        if not self.cfg or not self.collection or not self.name:
            logging.error("Config, Name or Paths is None. Not exporting anything")
            return

        if self.cfg.export_jpg_preview:
            self.export_jpeg_preview(self.collection.get_layers())

        if self.cfg.export_source:
            self.export_source()

        self.print_pen_move_distances(self.collection)

        fname = self._generate_filename()
        format = ExportFormatMappings.maps[self.cfg.type]

        separate_layers = self.collection.get_layers()

        if "pen_mapping" in self.collection.properties:
            self.export_copic_color_mapping(fname, separate_layers)

        for layer, pc in separate_layers.items():
            layer_fname = f"{fname}_{layer}"

            if format is ExportFormat.HPGL:
                self._export_hpgl(pc, layer_fname)
            elif format is ExportFormat.SVG:
                self._export_svg(pc, layer_fname)
            elif format is ExportFormat.GCODE:
                self._export_gcode(pc, layer_fname)
            elif format is ExportFormat.TEK:
                self._export_tek(pc, layer_fname)
            elif format is ExportFormat.DIGI:
                self._export_digi(pc, layer_fname)

    def _export_hpgl(self, pc: Collection, fname: str) -> None:
        hpgl_folder = DataDirHandler().hpgl(self.name)
        hpgl_renderer = HPGLRenderer(hpgl_folder)
        hpgl_renderer.add(pc)
        if self.cfg and self.cfg.optimize_hpgl_by_tsp:
            self.print_pen_move_distances(hpgl_renderer.collection)
            hpgl_renderer.optimize()
            self.print_pen_move_distances(hpgl_renderer.collection)
        hpgl_renderer.save(fname)

    def _export_svg(self, pc: Collection, fname: str) -> None:
        svg_dir = DataDirHandler().svg(self.name)
        bb = pc.bb()
        svg_renderer = SvgRenderer(svg_dir, bb.w, bb.h)
        svg_renderer.add(pc)
        svg_renderer.render()
        svg_renderer.save(fname)

    def _export_gcode(self, pc: Collection, fname: str) -> None:
        gcode_folder = DataDirHandler().gcode(self.name)
        gcode_renderer = GCodeRenderer(
            gcode_folder, feedrate_xy=self.gcode_speed or 2000, z_down=-6
        )
        gcode_renderer.render(pc)
        gcode_renderer.save(fname)

    def _export_tek(self, pc: Collection, fname: str) -> None:
        tek_folder = DataDirHandler().tek(self.name)
        tek_renderer = TektronixRenderer(tek_folder)
        tek_renderer.render(pc)
        tek_renderer.save(fname)

    def _export_digi(self, pc: Collection, fname: str) -> None:
        digi_folder = DataDirHandler().digi(self.name)
        digi_renderer = DigiplotRenderer(digi_folder)
        digi_renderer.render(pc)
        digi_renderer.save(fname)
