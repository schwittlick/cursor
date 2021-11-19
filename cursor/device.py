from cursor import data
from cursor import renderer

from enum import Enum
import wasabi

log = wasabi.Printer()


class MinMax:
    def __init__(self, minx: int, maxx: int, miny: int, maxy: int):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy


class PlotterType(Enum):
    ROLAND_DPX3300 = 0
    DIY_PLOTTER = 1
    AXIDRAW = 2
    HP_7475A_A4 = 3
    HP_7475A_A3 = 4
    ROLAND_DXY1200 = 5
    ROLAND_DXY980 = 6
    HP_7595A = 7
    ROLAND_PNC1000 = 8


class ExportFormat(Enum):
    JPG = 0
    SVG = 1
    GCODE = 2
    HPGL = 3


class ExportFormatMappings:
    maps = {
        PlotterType.ROLAND_DPX3300: ExportFormat.HPGL,
        PlotterType.DIY_PLOTTER: ExportFormat.GCODE,
        PlotterType.AXIDRAW: ExportFormat.SVG,
        PlotterType.HP_7475A_A3: ExportFormat.HPGL,
        PlotterType.HP_7475A_A4: ExportFormat.HPGL,
        PlotterType.ROLAND_DXY1200: ExportFormat.HPGL,
        PlotterType.ROLAND_DXY980: ExportFormat.HPGL,
        PlotterType.HP_7595A: ExportFormat.HPGL,
        PlotterType.ROLAND_PNC1000: ExportFormat.HPGL,
    }


class MinmaxMapping:
    maps = {
        PlotterType.ROLAND_DPX3300: MinMax(-17750, 16790, -11180, 11180),
        PlotterType.DIY_PLOTTER: MinMax(0, 3350, 0, -1715),
        PlotterType.AXIDRAW: MinMax(0, 0, 0, -0),  # todo: missing real bounds
        PlotterType.HP_7475A_A4: MinMax(0, 11040, 0, 7721),
        PlotterType.HP_7475A_A3: MinMax(0, 16158, 0, 11040),
        PlotterType.ROLAND_DXY1200: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.ROLAND_DXY980: MinMax(0, 16158, 0, 11040),
        PlotterType.HP_7595A: MinMax(-23160, 23160, -17602, 17602),
        PlotterType.ROLAND_PNC1000: MinMax(0, 0, 17200, 40000), # actually unlimited y
    }


class MinMaxMappingBB:
    from cursor import path

    maps = {
        PlotterType.ROLAND_DPX3300: path.BoundingBox(-17600, 33600, -11360, 23760),
        PlotterType.DIY_PLOTTER: path.BoundingBox(0, 3350, 0, -1715),
        PlotterType.AXIDRAW: MinMax(0, 0, 0, -0),  # todo: missing real bounds
        PlotterType.HP_7475A_A4: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.HP_7475A_A3: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.ROLAND_DXY1200: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.ROLAND_DXY980: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.ROLAND_PNC1000: MinMax(0, 0, 17200, 40000),  # todo: missing real bounds
    }


class PaperSize(Enum):
    PORTRAIT_36_48 = 0
    LANDSCAPE_48_36 = 1
    PORTRAIT_42_56 = 2
    LANDSCAPE_56_42 = 3
    PORTRAIT_50_70 = 4
    LANDSCAPE_70_50 = 5
    SQUARE_70_70 = 6
    PORTRAIT_70_100 = 7
    LANDSCAPE_100_70 = 8
    LANDSCAPE_A4 = 9
    PORTRAIT_A4 = 10
    LANDSCAPE_A1 = 11
    LANDSCAPE_A0 = 12
    PORTRAIT_A3 = 13
    LANDSCAPE_A3 = 14
    LANDSCAPE_80_50 = 15
    PORTRAIT_50_80 = 16


class PlotterName:
    names = {
        PlotterType.ROLAND_DPX3300: "dpx3300",
        PlotterType.AXIDRAW: "axidraw",
        PlotterType.DIY_PLOTTER: "custom",
        PlotterType.HP_7475A_A3: "hp7475a_a3",
        PlotterType.HP_7475A_A4: "hp7475a_a4",
        PlotterType.ROLAND_DXY1200: "dxy1200",
        PlotterType.ROLAND_DXY980: "dxy980",
        PlotterType.HP_7595A: "hp_draftmaster_sx",
        PlotterType.ROLAND_PNC1000: "roland_camm1",
    }


class PaperSizeName:
    names = {
        PaperSize.PORTRAIT_36_48: "portrait_36_48",
        PaperSize.LANDSCAPE_48_36: "landscape_48_36",
        PaperSize.PORTRAIT_42_56: "portrait_42_56",
        PaperSize.LANDSCAPE_56_42: "landscape_56_42",
        PaperSize.PORTRAIT_50_70: "portrait_50_70",
        PaperSize.LANDSCAPE_70_50: "landscape_70_50",
        PaperSize.SQUARE_70_70: "square_70_70",
        PaperSize.PORTRAIT_70_100: "portrait_70_100",
        PaperSize.LANDSCAPE_100_70: "landscape_100_70",
        PaperSize.LANDSCAPE_A4: "landscape_a4",
        PaperSize.PORTRAIT_A4: "portrait_a4",
        PaperSize.LANDSCAPE_A1: "landscape_a1",
        PaperSize.LANDSCAPE_A0: "landscape_a0",
        PaperSize.PORTRAIT_A3: "portrait_a3",
        PaperSize.LANDSCAPE_A3: "landscape_a3",
        PaperSize.LANDSCAPE_80_50: "landscape_80x50",
        PaperSize.PORTRAIT_50_80: "portrait_50_80",
    }


class Paper:
    sizes = {
        PaperSize.PORTRAIT_36_48: (360, 480),
        PaperSize.LANDSCAPE_48_36: (480, 360),
        PaperSize.PORTRAIT_42_56: (420, 560),
        PaperSize.LANDSCAPE_56_42: (560, 420),
        PaperSize.PORTRAIT_50_70: (500, 700),
        PaperSize.LANDSCAPE_70_50: (700, 500),
        PaperSize.SQUARE_70_70: (700, 700),
        PaperSize.PORTRAIT_70_100: (700, 1000),
        PaperSize.LANDSCAPE_100_70: (1000, 700),
        PaperSize.LANDSCAPE_A4: (297, 210),
        PaperSize.PORTRAIT_A4: (210, 297),
        PaperSize.LANDSCAPE_A1: (841, 594),
        PaperSize.LANDSCAPE_A0: (1189, 841),
        PaperSize.PORTRAIT_A3: (297, 420),
        PaperSize.LANDSCAPE_A3: (420, 297),
        PaperSize.LANDSCAPE_80_50: (800, 500),
        PaperSize.PORTRAIT_50_80: (500, 800),
    }


class XYFactors:
    fac = {
        PlotterType.ROLAND_DPX3300: (40, 40),
        PlotterType.DIY_PLOTTER: (2.85714, 2.90572),
        PlotterType.AXIDRAW: (3.704, 3.704),
        PlotterType.HP_7475A_A3: (40, 40),
        PlotterType.HP_7475A_A4: (40, 40),
        PlotterType.ROLAND_DXY1200: (40, 40),
        PlotterType.ROLAND_DXY980: (40, 40),
        PlotterType.HP_7595A: (40, 40),
        PlotterType.ROLAND_PNC1000: (40, 40),
    }


class Cfg:
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
    from cursor import path

    def __init__(self):
        self.__paths = None
        self.__cfg = None
        self.__name = None
        self.__suffix = None
        self.__hpgl_speed = None
        self.__gcode_speed = None
        self.__layer_pen_mapping = None

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
    def hpgl_speed(self) -> int:
        return self.__hpgl_speed

    @hpgl_speed.setter
    def hpgl_speed(self, t: int) -> None:
        self.__hpgl_speed = t

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

    def fit(self) -> None:
        # out_dim = tuple(
        #    _ * r
        #    for _, r in zip(
        #        Paper.sizes[self.cfg.dimension], XYFactors.fac[self.cfg.type]
        #    )
        # )
        if self.cfg.type is PlotterType.ROLAND_DPX3300:
            if self.cfg.margin < 35:
                log.warn(
                    f"Margin for dpx3300 to low: {self.cfg.margin}. Should be > 35mm."
                )
            self.paths.fit(
                Paper.sizes[self.cfg.dimension],
                xy_factor=XYFactors.fac[self.cfg.type],
                padding_mm=self.cfg.margin,
                center_point=(-880, 600),
                cutoff_mm=self.cfg.cutoff,
            )
        elif self.cfg.type is PlotterType.HP_7595A:
            self.paths.fit(
                Paper.sizes[self.cfg.dimension],
                xy_factor=XYFactors.fac[self.cfg.type],
                padding_mm=self.cfg.margin,
                center_point=(0, 0),
                cutoff_mm=self.cfg.cutoff,
            )
        else:
            self.paths.fit(
                Paper.sizes[self.cfg.dimension],
                xy_factor=XYFactors.fac[self.cfg.type],
                padding_mm=self.cfg.margin,
                cutoff_mm=self.cfg.cutoff,
            )

    def run(self, jpg: bool = False) -> None:
        if self.cfg is None or self.paths is None or self.name is None:
            log.fail("Config, Name or Paths is None. Not exporting anything")
            return

        # jpeg fitting roughly
        self.paths.fit(
            Paper.sizes[self.cfg.dimension],
            padding_mm=self.cfg.margin,
            cutoff_mm=self.cfg.cutoff,
        )

        if jpg:
            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                sizename = PaperSizeName.names[self.cfg.dimension]
                machinename = PlotterName.names[self.cfg.type]
                fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}"

                jpeg_folder = data.DataDirHandler().jpg(self.name)
                jpeg_renderer = renderer.JpegRenderer(jpeg_folder)
                jpeg_renderer.render(pc, scale=3.0)
                jpeg_renderer.save(f"{fname}_{layer}")

        self.fit()

        sizename = PaperSizeName.names[self.cfg.dimension]
        machinename = PlotterName.names[self.cfg.type]
        fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}"
        format = ExportFormatMappings.maps[self.cfg.type]

        if self.layer_pen_mapping is not None:
            if format is ExportFormat.HPGL:
                hpgl_folder = data.DataDirHandler().hpgl(self.name)
                if self.hpgl_speed:
                    hpgl_renderer = renderer.HPGLRenderer(
                        hpgl_folder,
                        speed=self.hpgl_speed,
                        layer_pen_mapping=self.layer_pen_mapping,
                    )
                else:
                    hpgl_renderer = renderer.HPGLRenderer(
                        hpgl_folder, layer_pen_mapping=self.layer_pen_mapping
                    )
                hpgl_renderer.render(self.paths)
                hpgl_renderer.save(f"{fname}_all")
        else:
            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                if format is ExportFormat.HPGL:
                    hpgl_folder = data.DataDirHandler().hpgl(self.name)
                    if self.hpgl_speed:
                        hpgl_renderer = renderer.HPGLRenderer(
                            hpgl_folder, speed=self.hpgl_speed
                        )
                    else:
                        hpgl_renderer = renderer.HPGLRenderer(hpgl_folder)
                    hpgl_renderer.render(pc)
                    hpgl_renderer.save(f"{fname}_{layer}")

                if format is ExportFormat.SVG:
                    svg_dir = data.DataDirHandler().svg(self.name)
                    svg_renderer = renderer.SvgRenderer(svg_dir)
                    svg_renderer.render(pc)
                    svg_renderer.save(f"{fname}_{layer}")

                if format is ExportFormat.GCODE:
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
                    gcode_renderer.save(f"{fname}_{layer}")


class SimpleExportWrapper:
    from cursor import path

    def ex(
        self,
        paths: path.PathCollection,
        ptype: PlotterType,
        psize: PaperSize,
        margin: int,
        name: str = "output_name",
        suffix: str = "",
        cutoff: int = None,
        hpgl_speed: int = None,
        gcode_speed: int = None,
        gcode_layer_pen_mapping=None,
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
        exp.hpgl_speed = hpgl_speed
        exp.gcode_speed = gcode_speed
        exp.layer_pen_mapping = gcode_layer_pen_mapping
        exp.run(True)
