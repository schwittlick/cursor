from cursor import renderer
from cursor import data
from cursor import device

import inspect
import hashlib
import wasabi
import pathlib

log = wasabi.Printer()


class Cfg:
    def __init__(self):
        self.__type = None
        self.__dimensions = None
        self.__margin = None
        self.__cutoff = None

    @property
    def type(self) -> device.PlotterType:
        return self.__type

    @type.setter
    def type(self, t: device.PlotterType) -> None:
        self.__type = t

    @property
    def dimension(self) -> device.PaperSize:
        return self.__dimensions

    @dimension.setter
    def dimension(self, t: device.PaperSize):
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
    from cursor import path

    def __init__(self):
        self.__paths = None
        self.__cfg = None
        self.__name = None
        self.__suffix = None
        self.__gcode_speed = None
        self.__layer_pen_mapping = None
        self.__linetype_mapping = None

    @property
    def paths(self) -> path.PathCollection:
        return self.__paths

    @paths.setter
    def paths(self, t: path.PathCollection) -> None:
        self.__paths = t

    @property
    def cfg(self) -> Cfg:
        return self.__cfg

    @cfg.setter
    def cfg(self, t: Cfg) -> None:
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

    def run(self, jpg: bool = False, source: bool = False) -> None:
        if self.cfg is None or self.paths is None or self.name is None:
            log.fail("Config, Name or Paths is None. Not exporting anything")
            return

        # jpeg fitting roughly
        self.paths.fit(
            device.Paper.sizes[self.cfg.dimension],
            padding_mm=self.cfg.margin,
            cutoff_mm=self.cfg.cutoff,
        )

        module = inspect.getmodule(inspect.stack()[2][0])
        ms = inspect.getsource(module)

        if jpg:
            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                sizename = device.PaperSizeName.names[self.cfg.dimension]
                machinename = device.PlotterName.names[self.cfg.type]
                fname = (
                    f"{self.name}_{self.suffix}_{sizename}_{machinename}_{layer}_"
                    f"{hashlib.sha256(ms.encode('utf-8')).hexdigest()}"
                )

                jpeg_folder = data.DataDirHandler().jpg(self.name)
                jpeg_renderer = renderer.JpegRenderer(jpeg_folder)
                jpeg_renderer.render(pc, scale=8.0)
                jpeg_renderer.save(f"{fname}")

        if source:
            source_folder = data.DataDirHandler().source(self.name)
            sizename = device.PaperSizeName.names[self.cfg.dimension]
            machinename = device.PlotterName.names[self.cfg.type]
            fname = (
                f"{self.name}_{self.suffix}_{sizename}_{machinename}_"
                f"{hashlib.sha256(ms.encode('utf-8')).hexdigest()}.py"
            )

            pathlib.Path(source_folder).mkdir(parents=True, exist_ok=True)
            log.good(f"Saved source to {source_folder / fname}")
            with open(source_folder / fname, "w") as file:
                file.write(ms)

        self.paths.fit(
            device.Paper.sizes[self.cfg.dimension],
            xy_factor=device.XYFactors.fac[self.cfg.type],
            padding_mm=self.cfg.margin,
            output_bounds=device.MinmaxMapping.maps[self.cfg.type],
            cutoff_mm=self.cfg.cutoff,
        )

        sizename = device.PaperSizeName.names[self.cfg.dimension]
        machinename = device.PlotterName.names[self.cfg.type]
        fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}_{hashlib.sha256(ms.encode('utf-8')).hexdigest()}"
        format = device.ExportFormatMappings.maps[self.cfg.type]
        if self.linetype_mapping and format is device.ExportFormat.HPGL:
            hpgl_folder = data.DataDirHandler().hpgl(self.name)
            hpgl_renderer = renderer.HPGLRenderer(
                hpgl_folder, line_type_mapping=self.linetype_mapping
            )
            hpgl_renderer.render(self.paths)
            hpgl_renderer.save(f"{fname}")
        if self.layer_pen_mapping is not None:
            if format is device.ExportFormat.HPGL:
                hpgl_folder = data.DataDirHandler().hpgl(self.name)

                hpgl_renderer = renderer.HPGLRenderer(
                    hpgl_folder, layer_pen_mapping=self.layer_pen_mapping
                )
                hpgl_renderer.render(self.paths)
                hpgl_renderer.save(f"{fname}")
        else:
            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                if format is device.ExportFormat.HPGL:
                    hpgl_folder = data.DataDirHandler().hpgl(self.name)
                    hpgl_renderer = renderer.HPGLRenderer(hpgl_folder)
                    hpgl_renderer.render(pc)
                    hpgl_renderer.save(f"{fname}_{layer}")

                if format is device.ExportFormat.SVG:
                    svg_dir = data.DataDirHandler().svg(self.name)
                    svg_renderer = renderer.SvgRenderer(svg_dir)
                    svg_renderer.render(pc)
                    svg_renderer.save(f"{fname}_{layer}")

                if format is device.ExportFormat.GCODE:
                    gcode_folder = data.DataDirHandler().gcode(self.name)
                    if self.gcode_speed:
                        gcode_renderer = renderer.GCodeRenderer(
                            gcode_folder, z_down=4.5
                        )
                    else:
                        gcode_renderer = renderer.GCodeRenderer(
                            gcode_folder, feedrate_xy=self.gcode_speed, z_down=4.5
                        )
                    gcode_renderer.render(pc)
                    gcode_renderer.save(f"{layer}_{fname}")

                if format is device.ExportFormat.TEK:
                    tek_folder = data.DataDirHandler().tek(self.name)
                    tek_renderer = renderer.TektronixRenderer(tek_folder)
                    tek_renderer.render(pc)
                    tek_renderer.save(f"{layer}_{fname}")

                if format is device.ExportFormat.DIGI:
                    digi_folder = data.DataDirHandler().digi(self.name)
                    digi_renderer = renderer.DigiplotRenderer(digi_folder)
                    digi_renderer.render(pc)
                    digi_renderer.save(f"{layer}_{fname}")


class SimpleExportWrapper:
    from cursor import path

    def ex(
        self,
        paths: path.PathCollection,
        ptype: device.PlotterType,
        psize: device.PaperSize,
        margin: int,
        name: str = "output_name",
        suffix: str = "",
        cutoff: int = None,
        gcode_speed: int = None,
        hpgl_pen_layer_mapping=None,
        hpgl_linetype_mapping=None,
        export_reversed=None
    ):
        cfg = Cfg()
        cfg.type = ptype
        cfg.dimension = psize
        cfg.margin = margin
        cfg.cutoff = cutoff

        # paths.clean()

        exp = Exporter()
        exp.cfg = cfg
        exp.paths = paths
        exp.name = name
        exp.suffix = str(suffix)
        exp.gcode_speed = gcode_speed
        exp.layer_pen_mapping = hpgl_pen_layer_mapping
        exp.linetype_mapping = hpgl_linetype_mapping
        exp.run(True, True)
        if export_reversed:
            exp.paths.reverse()
            exp.suffix = exp.suffix + "_reversed_"
            exp.run(True, True)
