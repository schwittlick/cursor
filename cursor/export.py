import random
import string
import logging

from cursor.algorithm.color.copic import Copic
from cursor.bb import BoundingBox
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
import inspect
import hashlib
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
            margin: int | None = None,
            cutoff: int | None = None,
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


class Exporter:
    def __init__(self, collection: Collection):
        self.collection = collection
        self.cfg = None
        self.name = None
        self.suffix = None
        self.gcode_speed = None
        self.keep_aspect_ratio = None

    def fit(self):
        self.collection.fit(
            output_bounds=MinmaxMapping.maps[self.cfg.type],
            xy_factor=XYFactors.fac[self.cfg.type],
            padding_mm=self.cfg.margin,
            cutoff_mm=self.cfg.cutoff,
            keep_aspect=self.keep_aspect_ratio,
        )

    def print_pen_move_distances(self, collection: Collection):
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

    def run(self) -> None:
        if self.cfg is None or self.collection is None or self.name is None:
            logging.error("Config, Name or Paths is None. Not exporting anything")
            return

        ms = self._file_content_of_caller()
        if self.cfg.export_jpg_preview:

            separate_layers = self.collection.get_layers()
            for layer, pc in separate_layers.items():
                machinename = PlotterName.names[self.cfg.type]
                h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
                hash = h[:4] + h[len(h) - 4:]
                fname = (
                    f"{self.name}_{self.suffix}_{machinename}_{layer}_"
                    f"{hash}"
                )

                jpeg_folder = DataDirHandler().jpg(self.name)
                bb = self.collection.bb()
                bb.scale(0.1)
                transformed = pc.transformed(BoundingBox(0, 0, bb.w, bb.h))
                # in case the BB is negative
                jpeg_renderer = JpegRenderer(jpeg_folder, w=int(bb.w), h=int(bb.h))
                jpeg_renderer.add(transformed)
                jpeg_renderer.render()
                jpeg_renderer.save(f"{fname}")

        if self.cfg.export_source:
            source_folder = DataDirHandler().source(self.name)
            machinename = PlotterName.names[self.cfg.type]
            h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
            hash = h[:4] + h[len(h) - 4:]
            fname = f"{self.name}_{self.suffix}_{machinename}_" f"{hash}.py"

            pathlib.Path(source_folder).mkdir(parents=True, exist_ok=True)
            logging.info(f"Saved source to {source_folder / fname}")
            with open(source_folder / fname, "w") as file:
                file.write(ms)

        self.print_pen_move_distances(self.collection)

        machinename = PlotterName.names[self.cfg.type]
        h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
        hash = h[:4] + h[len(h) - 4:]
        fname = f"{self.name}_{self.suffix}_{machinename}_{hash}"
        format = ExportFormatMappings.maps[self.cfg.type]

        separate_layers = self.collection.get_layers()

        # if "pen_mapping" in self.collection.properties.keys():
        #    pen_mapping_list = self.collection.properties["pen_mapping"]
        #    for layer_id in range(len(pen_mapping_list)):
        #        pen_mapping = pen_mapping_list[layer_id]

        # for pen in pen_mapping:
        #    metadata.write(f"Pen {pen[0]} -> {Copic().color(pen[1])}\n")

        for layer, pc in separate_layers.items():
            if format is ExportFormat.HPGL:
                hpgl_folder = DataDirHandler().hpgl(self.name)
                hpgl_renderer = HPGLRenderer(hpgl_folder)
                hpgl_renderer.add(pc)
                if self.cfg.optimize_hpgl_by_tsp:
                    self.print_pen_move_distances(hpgl_renderer.collection)
                    hpgl_renderer.optimize()
                    self.print_pen_move_distances(hpgl_renderer.collection)
                hpgl_renderer.save(f"{fname}_{layer}")

                if "pen_mapping" in self.collection.properties.keys():
                    pen_mapping = self.collection.properties["pen_mapping"][layer]
                    with open(hpgl_folder / f"{fname}_{layer}.txt",
                              "w") as metadata:
                        for pen_idx, color in pen_mapping.items():
                            metadata.write(f"Pen {pen_idx} -> {Copic().color(color)}\n")

            if format is ExportFormat.SVG:
                svg_dir = DataDirHandler().svg(self.name)
                bb = pc.bb()
                svg_renderer = SvgRenderer(svg_dir, bb.w, bb.h)
                svg_renderer.add(pc)
                svg_renderer.render()
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


class ExportWrapper:
    def __init__(
            self,
            paths: Collection,
            ptype: PlotterType,
            margin: int,
            name: str = "output_name",
            suffix: str = "",
            cutoff: int = None,
            gcode_speed: int = None,
            export_reversed=None,
            keep_aspect_ratio=False,
            export_jpg_preview=False
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

        self.config = ExportConfig(ptype, margin, cutoff, False, export_jpg_preview, False)

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
