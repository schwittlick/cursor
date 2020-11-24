import wasabi
from enum import Enum

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
    HP_7475A = 3
    ROLAND_DXY1200 = 3


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
        PlotterType.HP_7475A: ExportFormat.HPGL,
        PlotterType.ROLAND_DXY1200: ExportFormat.HPGL,
    }


class MinmaxMapping:
    maps = {
        PlotterType.ROLAND_DPX3300: MinMax(-17600, 16000, -11360, 12400),
        PlotterType.DIY_PLOTTER: MinMax(0, 3350, 0, -1715),
        PlotterType.AXIDRAW: MinMax(0, 0, 0, -0),  # todo: missing real bounds
        PlotterType.HP_7475A: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.ROLAND_DXY1200: MinMax(0, 0, 0, 0),  # todo: missing real bounds
    }


class MinMaxMappingBB:
    from cursor import path
    maps = {
        PlotterType.ROLAND_DPX3300: path.BoundingBox(-17600, 33600, -11360, 23760),
        PlotterType.DIY_PLOTTER: path.BoundingBox(0, 3350, 0, -1715),
        PlotterType.AXIDRAW: MinMax(0, 0, 0, -0),  # todo: missing real bounds
        PlotterType.HP_7475A: MinMax(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.ROLAND_DXY1200: MinMax(0, 0, 0, 0),  # todo: missing real bounds
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


class PlotterName:
    names = {
        PlotterType.ROLAND_DPX3300: "dpx3300",
        PlotterType.AXIDRAW: "axidraw",
        PlotterType.DIY_PLOTTER: "custom",
        PlotterType.HP_7475A: "hp7475a",
        PlotterType.ROLAND_DXY1200: "dxy1200",
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
    }


class XYFactors:
    fac = {
        PlotterType.ROLAND_DPX3300: (40, 40),
        PlotterType.DIY_PLOTTER: (2.85714, 2.90572),
        PlotterType.AXIDRAW: (3.704, 3.704),
    }


class Cfg:
    def __init__(self):
        self.__type = None
        self.__dimensions = None
        self.__margin = None

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


class Exporter:
    from cursor import path

    def __init__(self):
        self.__paths = None
        self.__cfg = None
        self.__name = None
        self.__suffix = None

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

    def fit(self) -> None:
        out_dim = tuple(
            l * r
            for l, r in zip(
                Paper.sizes[self.cfg.dimension], XYFactors.fac[self.cfg.type]
            )
        )

        if self.cfg.type is PlotterType.ROLAND_DPX3300:
            self.paths.fit(
                out_dim, xy_factor=XYFactors.fac[self.cfg.type], padding_mm=self.cfg.margin, center_point=(-880, 600)
            )
        else:
            self.paths.fit(
                out_dim, xy_factor=XYFactors.fac[self.cfg.type], padding_mm=self.cfg.margin
            )

    def run(self, jpg: bool = False) -> None:
        if self.cfg is None or self.paths is None or self.name is None:
            log.fail("Config, Name or Paths is None. Not exporting anything")
            return

        from cursor import data
        from cursor import renderer

        # jpeg fitting roughly
        self.paths.fit(Paper.sizes[self.cfg.dimension], padding_mm=self.cfg.margin)

        if jpg:
            separate_layers = self.paths.get_layers()
            for layer, pc in separate_layers.items():
                sizename = PaperSizeName.names[self.cfg.dimension]
                machinename = PlotterName.names[self.cfg.type]
                fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}"

                jpeg_folder = data.DataDirHandler().jpg(self.name)
                jpeg_renderer = renderer.JpegRenderer(jpeg_folder)
                jpeg_renderer.render(pc, scale=4.0)
                jpeg_renderer.save(f"{fname}_{layer}")

        self.fit()
        separate_layers = self.paths.get_layers()
        for layer, pc in separate_layers.items():
            sizename = PaperSizeName.names[self.cfg.dimension]
            machinename = PlotterName.names[self.cfg.type]
            fname = f"{self.name}_{self.suffix}_{sizename}_{machinename}"

            format = ExportFormatMappings.maps[self.cfg.type]
            if format is ExportFormat.HPGL:
                hpgl_folder = data.DataDirHandler().hpgl(self.name)
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
                gcode_renderer = renderer.GCodeRenderer(gcode_folder, z_down=4.5)
                gcode_renderer.render(pc)
                gcode_renderer.save(f"{fname}_{layer}")


class SimpleExportWrapper:
    from cursor import path

    def ex(self, paths: path.PathCollection, ptype: PlotterType, psize: PaperSize, margin: int, name: str,
           suffix: str = ""):
        cfg = Cfg()
        cfg.type = ptype
        cfg.dimension = psize
        cfg.margin = margin

        exp = Exporter()
        exp.cfg = cfg
        exp.paths = paths
        exp.name = name
        exp.suffix = str(suffix)
        exp.run(True)
