import random
import string

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

log = wasabi.Printer()


class Config:
    def __init__(self):
        self.__type = None
        self.__dimensions = None
        self.__margin = None
        self.__cutoff = None

    @property
    def type(self) -> PlotterType:
        return self.__type

    @type.setter
    def type(self, t: PlotterType) -> None:
        self.__type = t

    @property
    def dimension(self) -> PaperSize:
        return self.__dimensions

    @dimension.setter
    def dimension(self, t: PaperSize):
        self.__dimensions = t

    @property
    def margin(self) -> int:
        return self.__margin

    @margin.setter
    def margin(self, t: int):
        self.__margin = t

    @property
    def cutoff(self) -> int:
        return self.__cutoff

    @cutoff.setter
    def cutoff(self, t: int):
        self.__cutoff = t


class Exporter:
    def __init__(self):
        self.__paths = None
        self.__cfg = None
        self.__name = None
        self.__suffix = None
        self.__gcode_speed = None
        self.__layer_pen_mapping = None
        self.__linetype_mapping = None
        self.__keep_aspect_ratio = None

    @property
    def paths(self) -> Collection:
        return self.__paths

    @paths.setter
    def paths(self, t: Collection) -> None:
        self.__paths = t

    @property
    def cfg(self) -> Config:
        return self.__cfg

    @cfg.setter
    def cfg(self, t: Config) -> None:
        self.__cfg = t

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, t: str) -> None:
        self.__name = t

    @property
    def suffix(self) -> str:
        return self.__suffix

    @suffix.setter
    def suffix(self, t: str) -> None:
        self.__suffix = t

    @property
    def gcode_speed(self) -> int:
        return self.__gcode_speed

    @gcode_speed.setter
    def gcode_speed(self, t: int) -> None:
        self.__gcode_speed = t

    @property
    def layer_pen_mapping(self) -> dict:
        return self.__layer_pen_mapping

    @layer_pen_mapping.setter
    def layer_pen_mapping(self, m: dict) -> None:
        self.__layer_pen_mapping = m

    @property
    def linetype_mapping(self) -> dict:
        return self.__linetype_mapping

    @linetype_mapping.setter
    def linetype_mapping(self, m: dict) -> None:
        self.__linetype_mapping = m

    @property
    def keep_aspect_ratio(self) -> bool:
        return self.__keep_aspect_ratio

    @keep_aspect_ratio.setter
    def keep_aspect_ratio(self, kar: bool) -> None:
        self.__keep_aspect_ratio = kar

    def fit(self):
        self.paths.fit(
            Paper.sizes[self.cfg.dimension],
            xy_factor=XYFactors.fac[self.cfg.type],
            padding_mm=self.cfg.margin,
            output_bounds=MinmaxMapping.maps[self.cfg.type],
            cutoff_mm=self.cfg.cutoff,
            keep_aspect=self.keep_aspect_ratio
        )

    def run(self, jpg: bool = False, source: bool = False) -> None:
        if self.cfg is None or self.paths is None or self.name is None:
            log.fail("Config, Name or Paths is None. Not exporting anything")
            return

        module = inspect.getmodule(inspect.stack()[2][0])
        if module:
            ms = inspect.getsource(module)
        else:
            # this is being called from a ipython notebook
            # generating a random string to be hashed below.
            # this is very hacky :(
            ms = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        if jpg:
            # jpeg fitting roughly
            self.paths.fit(
                Paper.sizes[self.cfg.dimension],
                padding_mm=self.cfg.margin,
                cutoff_mm=self.cfg.cutoff,
                keep_aspect=self.keep_aspect_ratio
            )

            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                sizename = PaperSizeName.names[self.cfg.dimension]
                machinename = PlotterName.names[self.cfg.type]
                h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
                hash = h[:4] + h[len(h) - 4:]
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

        if source:
            source_folder = DataDirHandler().source(self.name)
            sizename = PaperSizeName.names[self.cfg.dimension]
            machinename = PlotterName.names[self.cfg.type]
            h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
            hash = h[:4] + h[len(h) - 4:]
            fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}_" f"{hash}.py"

            pathlib.Path(source_folder).mkdir(parents=True, exist_ok=True)
            log.good(f"Saved source to {source_folder / fname}")
            with open(source_folder / fname, "w") as file:
                file.write(ms)

        self.paths.fit(
            Paper.sizes[self.cfg.dimension],
            xy_factor=XYFactors.fac[self.cfg.type],
            padding_mm=self.cfg.margin,
            output_bounds=MinmaxMapping.maps[self.cfg.type],
            cutoff_mm=self.cfg.cutoff,
            keep_aspect=self.keep_aspect_ratio
        )

        unit_to_mm_factor = XYFactors.fac[self.cfg.type][0]
        distance_mm = int(self.paths.calc_travel_distance(unit_to_mm_factor))

        # here we need to add pen-up travel distance
        sum_dist_pen_up = 0
        for path_index in range(len(self.paths) - 1):
            end_p1 = self.paths[path_index].end_pos()
            start_p2 = self.paths[path_index + 1].start_pos()
            dist_pen_up = end_p1.distance(start_p2)
            sum_dist_pen_up += (dist_pen_up / unit_to_mm_factor)

        log.info(f"Total pen-down distance: {distance_mm / 1000}meters")
        log.info(f"Total pen-up distance: {int(sum_dist_pen_up / 1000)}meters")

        sizename = PaperSizeName.names[self.cfg.dimension]
        machinename = PlotterName.names[self.cfg.type]
        h = hashlib.sha256(ms.encode("utf-8")).hexdigest()
        hash = h[:4] + h[len(h) - 4:]
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
    def __init__(self, paths: Collection,
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
                 keep_aspect_ratio=False, ):
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

        self.config = Config()
        self.config.type = ptype
        self.config.dimension = psize
        self.config.margin = margin
        self.config.cutoff = cutoff

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
        self.exp.fit()

    def ex(self):
        self.exp.run(False, False)
        if self.export_reversed:
            self.exp.paths.reverse()
            self.exp.suffix = self.exp.suffix + "_reversed_"
            self.exp.run(True, True)
