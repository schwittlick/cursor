import random
import string
import logging

from cursor.collection import Collection
from cursor.data import DataDirHandler
from cursor.device import (
    PlotterType,
    PaperSize,
    Paper,
    PaperSizeName,
    PlotterName,
    MinmaxMapping,
    XYFactors,
    ExportFormatMappings,
    ExportFormat,
)
import inspect
import hashlib
import wasabi
import pathlib

from cursor.renderer.digi import DigiplotRenderer
from cursor.renderer.gcode import GCodeRenderer
from cursor.renderer.hpgl import HPGLRenderer
from cursor.renderer.jpg import JpegRenderer
from cursor.renderer.svg import SvgRenderer
from cursor.renderer.tektronix import TektronixRenderer
from cursor.timer import Timer


class ExportConfig:
    def __init__(
        self,
        type: PlotterType | None = None,
        dim: PaperSize | None = None,
        margin: int | None = None,
        cutoff: int | None = None,
        export_source: bool = False,
    ):
        self.type: PlotterType = type
        self.dimension = dim
        self.margin = margin
        self.cutoff = cutoff
        self.export_source = export_source


class Exporter:
    def __init__(self):
        self.paths = None
        self.cfg = None
        self.name = None
        self.suffix = None
        self.gcode_speed = None
        self.layer_pen_mapping = None
        self.linetype_mapping = None
        self.keep_aspect_ratio = None

    def fit(self):
        self.paths.fit(
            Paper.sizes[self.cfg.dimension],
            xy_factor=XYFactors.fac[self.cfg.type],
            padding_mm=self.cfg.margin,
            output_bounds=MinmaxMapping.maps[self.cfg.type],
            cutoff_mm=self.cfg.cutoff,
            keep_aspect=self.keep_aspect_ratio,
        )

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

    def run(self, jpg: bool = False) -> None:
        if self.cfg is None or self.paths is None or self.name is None:
            logging.error("Config, Name or Paths is None. Not exporting anything")
            return

        ms = self._file_content_of_caller()
        if jpg:
            # jpeg fitting roughly
            self.paths.fit(
                Paper.sizes[self.cfg.dimension],
                padding_mm=self.cfg.margin,
                cutoff_mm=self.cfg.cutoff,
                keep_aspect=self.keep_aspect_ratio,
            )

            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                sizename = PaperSizeName.names[self.cfg.dimension]
                machinename = PlotterName.names[self.cfg.type]
                h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
                hash = h[:4] + h[len(h) - 4 :]
                fname = (
                    f"{self.name}_{self.suffix}_{sizename}_{machinename}_{layer}_"
                    f"{hash}"
                )

                jpeg_folder = DataDirHandler().jpg(self.name)
                w, h = Paper.sizes[self.cfg.dimension]
                scale = 2
                jpeg_renderer = JpegRenderer(jpeg_folder, w=w * scale, h=h * scale)
                jpeg_renderer.add(pc)
                jpeg_renderer.render(scale=scale)
                jpeg_renderer.save(f"{fname}")

        if self.cfg.export_source:
            source_folder = DataDirHandler().source(self.name)
            sizename = PaperSizeName.names[self.cfg.dimension]
            machinename = PlotterName.names[self.cfg.type]
            h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
            hash = h[:4] + h[len(h) - 4 :]
            fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}_" f"{hash}.py"

            pathlib.Path(source_folder).mkdir(parents=True, exist_ok=True)
            logging.info(f"Saved source to {source_folder / fname}")
            with open(source_folder / fname, "w") as file:
                file.write(ms)

        unit_to_mm_factor = XYFactors.fac[self.cfg.type][0]
        distance_mm = int(self.paths.calc_travel_distance(unit_to_mm_factor))

        # here we need to add pen-up travel distance
        sum_dist_pen_up = 0
        for path_index in range(len(self.paths) - 1):
            end_p1 = self.paths[path_index].end_pos()
            start_p2 = self.paths[path_index + 1].start_pos()
            dist_pen_up = end_p1.distance(start_p2)
            sum_dist_pen_up += dist_pen_up / unit_to_mm_factor

        logging.info(f"Total pen-down distance: {distance_mm / 1000}meters")
        logging.info(f"Total pen-up distance: {int(sum_dist_pen_up / 1000)}meters")

        sizename = PaperSizeName.names[self.cfg.dimension]
        machinename = PlotterName.names[self.cfg.type]
        h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
        hash = h[:4] + h[len(h) - 4 :]
        fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}_{hash}"
        format = ExportFormatMappings.maps[self.cfg.type]
        if self.linetype_mapping and format is ExportFormat.HPGL:
            hpgl_folder = DataDirHandler().hpgl(self.name)
            hpgl_renderer = HPGLRenderer(
                hpgl_folder, line_type_mapping=self.linetype_mapping
            )
            hpgl_renderer.add(self.paths)
            hpgl_renderer.save(f"{fname}")
        if self.layer_pen_mapping is not None:
            if format is ExportFormat.HPGL:
                hpgl_folder = DataDirHandler().hpgl(self.name)

                hpgl_renderer = HPGLRenderer(
                    hpgl_folder, layer_pen_mapping=self.layer_pen_mapping
                )
                hpgl_renderer.add(self.paths)
                hpgl_renderer.save(f"{fname}")
        else:
            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                if format is ExportFormat.HPGL:
                    hpgl_folder = DataDirHandler().hpgl(self.name)
                    hpgl_renderer = HPGLRenderer(hpgl_folder)
                    hpgl_renderer.add(pc)
                    hpgl_renderer.save(f"{fname}_{layer}")

                if format is ExportFormat.SVG:
                    svg_dir = DataDirHandler().svg(self.name)
                    svg_renderer = SvgRenderer(svg_dir)
                    svg_renderer.render(pc)
                    svg_renderer.save(f"{fname}_{layer}")

                if format is ExportFormat.GCODE:
                    gcode_folder = DataDirHandler().gcode(self.name)
                    if self.gcode_speed:
                        gcode_renderer = GCodeRenderer(gcode_folder, z_down=4.5)
                    else:
                        gcode_renderer = GCodeRenderer(
                            gcode_folder, feedrate_xy=self.gcode_speed, z_down=4.5
                        )
                    gcode_renderer.render(pc)
                    gcode_renderer.save(f"{layer}_{fname}")

                if format is ExportFormat.TEK:
                    tek_folder = DataDirHandler().tek(self.name)
                    tek_renderer = TektronixRenderer(tek_folder)
                    tek_renderer.render(pc)
                    tek_renderer.save(f"{layer}_{fname}")

                if format is ExportFormat.DIGI:
                    digi_folder = DataDirHandler().digi(self.name)
                    digi_renderer = DigiplotRenderer(digi_folder)
                    digi_renderer.render(pc)
                    digi_renderer.save(f"{layer}_{fname}")


def save_wrapper(pc, projname, fname):
    jpeg_folder = DataDirHandler().jpg(projname)
    jpeg_renderer = JpegRenderer(jpeg_folder)

    jpeg_renderer.add(pc)
    jpeg_renderer.render(scale=1.0)
    jpeg_renderer.save(fname)

    svg_folder = DataDirHandler().svg(projname)
    svg_renderer = SvgRenderer(svg_folder)

    svg_renderer.render(pc)
    svg_renderer.save(fname)


def save_wrapper_jpeg(pc, projname, fname, scale=4.0, thickness=3):
    folder = DataDirHandler().jpg(projname)
    jpeg_renderer = JpegRenderer(folder, w=int(1920 * scale), h=int(1080 * scale))
    jpeg_renderer.add(pc)
    jpeg_renderer.render(scale=scale)
    jpeg_renderer.save(fname)


class ExportWrapper:
    def __init__(
        self,
        paths: Collection,
        ptype: PlotterType,
        psize: PaperSize,
        margin: int,
        name: str = "output_name",
        suffix: str = "",
        cutoff: int = None,
        gcode_speed: int = None,
        hpgl_pen_layer_mapping=None,
        hpgl_linetype_mapping=None,
        export_reversed=None,
        keep_aspect_ratio=False,
    ):
        self.paths = paths
        self.ptype = ptype
        self.psize = psize
        self.margin = margin
        self.name = name
        self.suffix = suffix
        self.cutoff = cutoff
        self.gcode_speed = gcode_speed
        self.hpgl_pen_layer_mapping = hpgl_pen_layer_mapping
        self.hpgl_linetype_mapping = hpgl_linetype_mapping
        self.export_reversed = export_reversed
        self.keep_aspect_ratio = keep_aspect_ratio

        self.config = ExportConfig(ptype, psize, margin, cutoff, False)

        self.exp = Exporter()
        self.exp.cfg = self.config
        self.exp.paths = paths
        self.exp.name = name
        self.exp.suffix = str(suffix)
        self.exp.gcode_speed = gcode_speed
        self.exp.layer_pen_mapping = hpgl_pen_layer_mapping
        self.exp.linetype_mapping = hpgl_linetype_mapping
        self.exp.keep_aspect_ratio = keep_aspect_ratio

    def fit(self):
        timer = Timer()
        self.exp.fit()
        timer.print_elapsed("ExportWrapper: fit()")

    def ex(self):
        timer = Timer()
        self.exp.run(False)
        if self.export_reversed:
            self.exp.paths.reverse()
            self.exp.suffix = self.exp.suffix + "_reversed_"
            self.exp.run(True)
        timer.print_elapsed("ExportWrapper: ex()")
