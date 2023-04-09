from enum import Enum

import wasabi

from cursor.bb import BoundingBox as BB

log = wasabi.Printer()


class PlotterType(Enum):
    def __str__(self):
        return self.name

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
    HP_7550A = 18
    HP_7595A_A2 = 19
    ROLAND_PNC1000_50x100 = 20
    HP_7595A_A0 = 21
    HP_7596A = 22


class ExportFormat(Enum):
    JPG = 0
    SVG = 1
    GCODE = 2
    HPGL = 3
    TEK = 4
    DIGI = 5


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
        PlotterType.HP_7550A: ExportFormat.HPGL,
        PlotterType.HP_7595A_A2: ExportFormat.HPGL,
        PlotterType.ROLAND_PNC1000_50x100: ExportFormat.HPGL,
        PlotterType.HP_7595A_A0: ExportFormat.HPGL,
        PlotterType.HP_7596A: ExportFormat.HPGL,

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
    PORTRAIT_50_100 = 21


class MinmaxMapping:
    maps = {
        PlotterType.ROLAND_DPX3300: BB(-16920, -11180, 16340, 11180),
        PlotterType.ROLAND_DPX3300_A2: BB(-16920, -11180, 5440, 4629),
        PlotterType.ROLAND_DPX3300_A3: BB(-16920, -11180, -1112, -3276),
        PlotterType.DIY_PLOTTER: BB(0, 0, 3350, -1715),
        PlotterType.AXIDRAW: BB(0, 0, 0, 0),  # todo: missing real bounds
        PlotterType.HP_7475A_A4: BB(0, 0, 11040, 7721),
        PlotterType.HP_7475A_A3: BB(0, 0, 16158, 11040),
        PlotterType.ROLAND_DXY1200: BB(0, 0, 16158, 11040),  # todo: missing real bounds
        PlotterType.ROLAND_DXY980: BB(0, 0, 16158, 11040),
        # PlotterType.HP_7595A_A0: BB(-23160, -17602, 23160 + 1160, 17602),
        PlotterType.HP_7595A: BB(-16090, -11684, 16090, 11684),
        # HP_7595A: minimum 35mm padding
        PlotterType.ROLAND_PNC1000: BB(0, 0, 18800, 40000),  # actually unlimited y
        PlotterType.ROLAND_PNC1000_50x100: BB(260, 560, 18700, 39000),  # for 50x100cm paper centered
        PlotterType.HP_7595A_A3: BB(-7728, -5752, 7728 + 960, 5752),
        PlotterType.HP_7595A_A0: BB(-21760, -15400, 22880, 15480),
        PlotterType.TEKTRONIX_4662: BB(0, 0, 4095, 2731),
        # tekronix: 10x15 inches (25.4 x 38.1 cm)
        PlotterType.HP_7596B: BB(-15500, -11100, 15500 + 22 * 40, 11100),
        PlotterType.HP_7596A: BB(-16100, -11600, 16100, 11600),

        PlotterType.HP_7596B_A3: BB(-6800, -5250, 6800, 5250),
        PlotterType.HP_7596B_25_25: BB(-4310, -3444, 4310 + 800, 3444),
        PlotterType.DIGIPLOT_A1: BB(0, 0, 33600, 23700),
        PlotterType.HP_7470A: BB(0, 0, 10900, 7650),
        PlotterType.HP_7550A: BB(0, 0, 15970, 10870),
        PlotterType.HP_7595A_A2: BB(-11684, -7729 - 960, 11684, 7729),
    }


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
        PlotterType.HP_7550A: "hp7550a",
        PlotterType.HP_7595A_A2: "hp7595a_draftmaster_sx_a2",
        PlotterType.ROLAND_PNC1000_50x100: "roland_pnc1000",
        PlotterType.HP_7595A_A0: "hp7595a_draftmaster_sx_a0",
        PlotterType.HP_7596A: "hp7596a_draftmaster_II_a1",
    }


class PlotterHpglNames:
    names = {
        PlotterType.ROLAND_DPX3300: "-",
        PlotterType.ROLAND_DPX3300_A2: "-",
        PlotterType.ROLAND_DPX3300_A3: "-",
        PlotterType.AXIDRAW: "-",
        PlotterType.DIY_PLOTTER: "-",
        PlotterType.HP_7475A_A3: "7475A",
        PlotterType.HP_7475A_A4: "7475A",
        PlotterType.ROLAND_DXY1200: "DXY-1200",
        PlotterType.ROLAND_DXY980: "DXY-980",
        PlotterType.HP_7595A: "7595A",
        PlotterType.ROLAND_PNC1000: "-",
        PlotterType.HP_7595A_A3: "7595A",
        PlotterType.TEKTRONIX_4662: "-",
        PlotterType.HP_7596B: "7596A",
        PlotterType.HP_7596B_A3: "7596A",
        PlotterType.HP_7596B_25_25: "7596A",
        PlotterType.DIGIPLOT_A1: "-",
        PlotterType.HP_7470A: "7470A",
        PlotterType.HP_7550A: "7550A",
        PlotterType.HP_7595A_A2: "7595A",
        PlotterType.ROLAND_PNC1000_50x100: "-",
        PlotterType.HP_7595A_A0: "7595A",
        PlotterType.HP_7596A: "7596A",
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
        PlotterType.HP_7550A: (40, 40),
        PlotterType.HP_7595A_A2: (40, 39.5),
        PlotterType.ROLAND_PNC1000_50x100: (40.04, 40.04),
        PlotterType.HP_7595A_A0: (39.9, 40.04),
        PlotterType.HP_7596A: (40.0, 40.0),
    }


class MaxSpeed:
    fac = {
        PlotterType.ROLAND_DPX3300: 40,
        PlotterType.ROLAND_DPX3300_A2: 40,
        PlotterType.ROLAND_DPX3300_A3: 40,
        PlotterType.DIY_PLOTTER: 1,
        PlotterType.AXIDRAW: 1,
        PlotterType.HP_7475A_A3: 40,
        PlotterType.HP_7475A_A4: 40,
        PlotterType.ROLAND_DXY1200: 40,
        PlotterType.ROLAND_DXY980: 40,
        PlotterType.HP_7595A: 110,
        PlotterType.ROLAND_PNC1000: 40,
        PlotterType.HP_7595A_A3: 40,
        PlotterType.TEKTRONIX_4662: 1,
        PlotterType.HP_7596B: 110,
        PlotterType.HP_7596B_A3: 110,
        PlotterType.HP_7596B_25_25: 110,
        PlotterType.DIGIPLOT_A1: 1,
        PlotterType.HP_7470A: 40,
        PlotterType.HP_7550A: 80,
        PlotterType.HP_7595A_A2: 110,
        PlotterType.ROLAND_PNC1000_50x100: 40,
        PlotterType.HP_7595A_A0: 110,
        PlotterType.HP_7596A: 110,
    }


class BufferSize:
    fac = {
        PlotterType.ROLAND_DPX3300: 0,  # 0 = not tested
        PlotterType.ROLAND_DPX3300_A2: 0,
        PlotterType.ROLAND_DPX3300_A3: 0,
        PlotterType.DIY_PLOTTER: 1,
        PlotterType.AXIDRAW: 1,
        PlotterType.HP_7475A_A3: 512,
        PlotterType.HP_7475A_A4: 512,
        PlotterType.ROLAND_DXY1200: 0,
        PlotterType.ROLAND_DXY980: 0,
        PlotterType.HP_7595A: 1024,
        PlotterType.ROLAND_PNC1000: 0,
        PlotterType.HP_7595A_A3: 1024,
        PlotterType.TEKTRONIX_4662: 0,
        PlotterType.HP_7596B: 1024,
        PlotterType.HP_7596B_A3: 1024,
        PlotterType.HP_7596B_25_25: 1024,
        PlotterType.DIGIPLOT_A1: 0,
        PlotterType.HP_7470A: 256,
        PlotterType.HP_7550A: 512,
        PlotterType.HP_7595A_A2: 1024,
        PlotterType.ROLAND_PNC1000_50x100: 0,
        PlotterType.HP_7595A_A0: 1024,
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
        PaperSize.PORTRAIT_50_100: "portrait_50x100",
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
        PaperSize.LANDSCAPE_A0: (1119, 771),
        PaperSize.PORTRAIT_A3: (297, 420),
        PaperSize.LANDSCAPE_A3: (420, 297),
        PaperSize.LANDSCAPE_80_50: (800, 500),
        PaperSize.PORTRAIT_50_80: (500, 800),
        PaperSize.LANDSCAPE_A2: (594, 420),
        PaperSize.SQUARE_59_59: (590, 590),
        PaperSize.SQUARE_25_25: (215, 170),
        PaperSize.LANDSCAPE_A1_HP_7596B: (776, 555),
        PaperSize.PORTRAIT_50_100: (460, 960),
    }
