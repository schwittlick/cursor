import cursor.bb

from enum import Enum
import wasabi

log = wasabi.Printer()


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
    ROLAND_DPX3300_A2 = 9
    ROLAND_DPX3300_A3 = 10
    HP_7595A_A3 = 11
    TEKTRONIX_4662 = 12
    HP_7596B = 13
    HP_7596B_25_25 = 14
    HP_7596B_A3 = 15
    DIGIPLOT_A1 = 16
    HP_7470A = 17


class ExportFormat(Enum):
    JPG = 0
    SVG = 1
    GCODE = 2
    HPGL = 3
    TEK = 4


class ExportFormatMappings:
    maps = {
        PlotterType.ROLAND_DPX3300: ExportFormat.HPGL,
        PlotterType.ROLAND_DPX3300_A2: ExportFormat.HPGL,
        PlotterType.ROLAND_DPX3300_A3: ExportFormat.HPGL,
        PlotterType.DIY_PLOTTER: ExportFormat.GCODE,
        PlotterType.AXIDRAW: ExportFormat.SVG,
        PlotterType.HP_7475A_A3: ExportFormat.HPGL,
        PlotterType.HP_7475A_A4: ExportFormat.HPGL,
        PlotterType.ROLAND_DXY1200: ExportFormat.HPGL,
        PlotterType.ROLAND_DXY980: ExportFormat.HPGL,
        PlotterType.HP_7595A: ExportFormat.HPGL,
        PlotterType.ROLAND_PNC1000: ExportFormat.HPGL,
        PlotterType.HP_7595A_A3: ExportFormat.HPGL,
        PlotterType.TEKTRONIX_4662: ExportFormat.TEK,
        PlotterType.HP_7596B: ExportFormat.HPGL,
        PlotterType.HP_7596B_A3: ExportFormat.HPGL,
        PlotterType.HP_7596B_25_25: ExportFormat.HPGL,
        PlotterType.DIGIPLOT_A1: ExportFormat.DIGI,
        PlotterType.HP_7470A: ExportFormat.HPGL,
    }


class MinmaxMapping:
    maps = {
        PlotterType.ROLAND_DPX3300: cursor.bb.BoundingBox(-16920, -11180, 16340, 11180),
        PlotterType.ROLAND_DPX3300_A2: cursor.bb.BoundingBox(
            -16920, -11180, 5440, 4629
        ),
        PlotterType.ROLAND_DPX3300_A3: cursor.bb.BoundingBox(
            -16920, -11180, -1112, -3276
        ),
        PlotterType.DIY_PLOTTER: cursor.bb.BoundingBox(0, 0, 3350, -1715),
        PlotterType.AXIDRAW: cursor.bb.BoundingBox(
            0, 0, 0, -0
        ),  # todo: missing real bounds
        PlotterType.HP_7475A_A4: cursor.bb.BoundingBox(0, 0, 11040, 7721),
        PlotterType.HP_7475A_A3: cursor.bb.BoundingBox(0, 0, 16158, 11040),
        PlotterType.ROLAND_DXY1200: cursor.bb.BoundingBox(
            0, 0, 0, 0
        ),  # todo: missing real bounds
        PlotterType.ROLAND_DXY980: cursor.bb.BoundingBox(0, 0, 16158, 11040),
        PlotterType.HP_7595A: cursor.bb.BoundingBox(
            -23160, -17602, 23160 + 1160, 17602
        ),  # minimum 35mm padding
        PlotterType.ROLAND_PNC1000: cursor.bb.BoundingBox(
            0, 0, 17200, 40000
        ),  # actually unlimited y
        PlotterType.HP_7595A_A3: cursor.bb.BoundingBox(-7728, -5752, 7728 + 960, 5752),
        PlotterType.TEKTRONIX_4662: cursor.bb.BoundingBox(
            0, 0, 4095, 2731
        ),  # 10x15 inches (25.4 x 38.1 cm)
        PlotterType.HP_7596B: cursor.bb.BoundingBox(
            -15500, -11100, 15500 + 22 * 40, 11100
        ),
        PlotterType.HP_7596B_A3: cursor.bb.BoundingBox(-6800, -5250, 6800, 5250),
        PlotterType.HP_7596B_25_25: cursor.bb.BoundingBox(
            -4310, -3444, 4310 + 800, 3444
        ),
        PlotterType.DIGIPLOT_A1: cursor.bb.BoundingBox(0, 0, 33600, 23700),
        PlotterType.HP_7470A: cursor.bb.BoundingBox(0, 0, 10900, 7650)
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
    LANDSCAPE_A2 = 17
    SQUARE_59_59 = 18
    SQUARE_25_25 = 19
    LANDSCAPE_A1_HP_7596B = 20


class PlotterName:
    names = {
        PlotterType.ROLAND_DPX3300: "dpx3300",
        PlotterType.ROLAND_DPX3300_A2: "dpx3300_a2",
        PlotterType.ROLAND_DPX3300_A3: "dpx3300_a3",
        PlotterType.AXIDRAW: "axidraw",
        PlotterType.DIY_PLOTTER: "custom",
        PlotterType.HP_7475A_A3: "hp7475a_a3",
        PlotterType.HP_7475A_A4: "hp7475a_a4",
        PlotterType.ROLAND_DXY1200: "dxy1200",
        PlotterType.ROLAND_DXY980: "dxy980",
        PlotterType.HP_7595A: "hp7595a_draftmaster_sx",
        PlotterType.ROLAND_PNC1000: "roland_camm1",
        PlotterType.HP_7595A_A3: "hp7595a_draftmaster_sx_a3",
        PlotterType.TEKTRONIX_4662: "tektronix4662",
        PlotterType.HP_7596B: "hp7596b_draftmaster_rxplus",
        PlotterType.HP_7596B_A3: "hp7596b_draftmaster_rxplus_a3",
        PlotterType.HP_7596B_25_25: "hp7596b_draftmaster_rxplus_2525",
        PlotterType.DIGIPLOT_A1: "digiplot_a1",
        PlotterType.HP_7470A: "hp7470a",
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
        PaperSize.LANDSCAPE_A2: "landscape_a2",
        PaperSize.SQUARE_59_59: "square_59_59",
        PaperSize.SQUARE_25_25: "square_25_25",
        PaperSize.LANDSCAPE_A1_HP_7596B: "landscape_a1",
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
        PaperSize.LANDSCAPE_A2: (594, 420),
        PaperSize.SQUARE_59_59: (590, 590),
        PaperSize.SQUARE_25_25: (215, 170),
        PaperSize.LANDSCAPE_A1_HP_7596B: (776, 555),
    }


class XYFactors:
    fac = {
        PlotterType.ROLAND_DPX3300: (40, 40),
        PlotterType.ROLAND_DPX3300_A2: (40, 40),
        PlotterType.ROLAND_DPX3300_A3: (40, 40),
        PlotterType.DIY_PLOTTER: (2.85714, 2.90572),
        PlotterType.AXIDRAW: (3.704, 3.704),
        PlotterType.HP_7475A_A3: (40, 40),
        PlotterType.HP_7475A_A4: (40, 40),
        PlotterType.ROLAND_DXY1200: (40, 40),
        PlotterType.ROLAND_DXY980: (40, 40),
        PlotterType.HP_7595A: (40, 40),
        PlotterType.ROLAND_PNC1000: (40, 40),
        PlotterType.HP_7595A_A3: (37, 37),
        PlotterType.TEKTRONIX_4662: (9.75, 9.19525),
        PlotterType.HP_7596B: (39.948, 40),
        PlotterType.HP_7596B_A3: (39.948, 40),
        PlotterType.HP_7596B_25_25: (40, 40),
        PlotterType.DIGIPLOT_A1: (40, 40),
        PlotterType.HP_7470A: (40, 40),
    }
