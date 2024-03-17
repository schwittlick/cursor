from __future__ import annotations

from enum import Enum, auto

import wasabi

from cursor.bb import BoundingBox as BB

log = wasabi.Printer()


class PlotterConfig:
    def __init__(self, type: PlotterType):
        self.type = type
        self.bb = MinmaxMapping.maps[type]


class PlotterType(Enum):
    def __str__(self):
        return self.name

    ROLAND_DPX3300_A1 = auto()
    ROLAND_DPX3300_A2 = auto()
    ROLAND_DPX3300_A3 = auto()

    HP_7550A_A3 = auto()
    HP_7550A_A4 = auto()

    HP_7475A_A4 = auto()
    HP_7475A_A3 = auto()

    HP_7470A_A4 = auto()

    HP_DM_RX_PLUS_A0 = auto()
    HP_DM_RX_PLUS_100x70cm = auto()
    HP_DM_RX_PLUS_A1 = auto()
    HP_DM_RX_PLUS_A2 = auto()
    HP_DM_RX_PLUS_A3 = auto()

    HP_DM_II_A1 = auto()
    HP_DM_II_A3 = auto()

    HP_DM_SX_A1 = auto()
    HP_DM_SX_A3 = auto()

    MUTOH_XP500_100x70cm = auto()
    MUTOH_XP500_500x297mm = auto()
    MUTOH_XP500_A1 = auto()
    MUTOH_XP500_A2 = auto()
    MUTOH_XP500_A3 = auto()

    DIY_PLOTTER = auto()
    AXIDRAW = auto()

    ROLAND_DXY1200_A3 = auto()
    ROLAND_DXY1200_A3_EXPANDED = auto()
    ROLAND_DXY980 = auto()
    ROLAND_PNC1000 = auto()
    TEKTRONIX_4662 = auto()
    DIGIPLOT_A1 = auto()
    ROLAND_PNC1000_50x100 = auto()
    HP_7570A_A1 = auto()


class ExportFormat(Enum):
    JPG = auto()
    SVG = auto()
    GCODE = auto()
    HPGL = auto()
    TEK = auto()
    DIGI = auto()


class ExportFormatMappings:
    maps = {
        PlotterType.ROLAND_DPX3300_A1: ExportFormat.HPGL,
        PlotterType.ROLAND_DPX3300_A2: ExportFormat.HPGL,
        PlotterType.ROLAND_DPX3300_A3: ExportFormat.HPGL,

        PlotterType.HP_7550A_A3: ExportFormat.HPGL,
        PlotterType.HP_7550A_A4: ExportFormat.HPGL,

        PlotterType.HP_7475A_A3: ExportFormat.HPGL,
        PlotterType.HP_7475A_A4: ExportFormat.HPGL,

        PlotterType.HP_7470A_A4: ExportFormat.HPGL,

        PlotterType.HP_DM_RX_PLUS_A0: ExportFormat.HPGL,
        PlotterType.HP_DM_RX_PLUS_100x70cm: ExportFormat.HPGL,
        PlotterType.HP_DM_RX_PLUS_A1: ExportFormat.HPGL,
        PlotterType.HP_DM_RX_PLUS_A2: ExportFormat.HPGL,
        PlotterType.HP_DM_RX_PLUS_A3: ExportFormat.HPGL,

        PlotterType.HP_DM_SX_A1: ExportFormat.HPGL,
        PlotterType.HP_DM_SX_A3: ExportFormat.HPGL,

        PlotterType.HP_DM_II_A1: ExportFormat.HPGL,
        PlotterType.HP_DM_II_A3: ExportFormat.HPGL,

        PlotterType.MUTOH_XP500_100x70cm: ExportFormat.HPGL,
        PlotterType.MUTOH_XP500_500x297mm: ExportFormat.HPGL,
        PlotterType.MUTOH_XP500_A1: ExportFormat.HPGL,
        PlotterType.MUTOH_XP500_A2: ExportFormat.HPGL,
        PlotterType.MUTOH_XP500_A3: ExportFormat.HPGL,

        PlotterType.DIY_PLOTTER: ExportFormat.GCODE,
        PlotterType.AXIDRAW: ExportFormat.SVG,

        PlotterType.ROLAND_DXY1200_A3: ExportFormat.HPGL,
        PlotterType.ROLAND_DXY980: ExportFormat.HPGL,
        PlotterType.ROLAND_PNC1000: ExportFormat.HPGL,
        PlotterType.TEKTRONIX_4662: ExportFormat.TEK,

        PlotterType.DIGIPLOT_A1: ExportFormat.DIGI,
        PlotterType.ROLAND_PNC1000_50x100: ExportFormat.HPGL,

        PlotterType.HP_7570A_A1: ExportFormat.HPGL,
    }


class PaperSize(Enum):
    PORTRAIT_36_48 = auto()
    LANDSCAPE_48_36 = auto()
    PORTRAIT_42_56 = auto()
    LANDSCAPE_56_42 = auto()
    PORTRAIT_50_70 = auto()
    LANDSCAPE_70_50 = auto()
    SQUARE_70_70 = auto()
    PORTRAIT_70_100 = auto()
    LANDSCAPE_100_70 = auto()
    LANDSCAPE_A4 = auto()
    PORTRAIT_A4 = auto()
    LANDSCAPE_A1 = auto()
    LANDSCAPE_A0 = auto()
    PORTRAIT_A3 = auto()
    LANDSCAPE_A3 = auto()
    LANDSCAPE_80_50 = auto()
    PORTRAIT_50_80 = auto()
    LANDSCAPE_A2 = auto()
    SQUARE_59_59 = auto()
    SQUARE_25_25 = auto()
    LANDSCAPE_A1_HP_7596B = auto()
    PORTRAIT_50_100 = auto()
    PHOTO_PAPER_240_178_LANDSCAPE = auto()
    PHOTO_PAPER_250_200_LANDSCAPE = auto()
    PHOTO_PAPER_400_300_LANDSCAPE = auto()
    PHOTO_PAPER_600_500_LANDSCAPE = auto()


class MinmaxMapping:
    maps = {
        PlotterType.ROLAND_DPX3300_A1: BB(-16920, -11180, 16340, 11180),
        PlotterType.ROLAND_DPX3300_A2: BB(-16920, -11180, 5440, 4629),
        PlotterType.ROLAND_DPX3300_A3: BB(-16920, -11180, -1112, -3276),

        PlotterType.HP_7550A_A3: BB(0, 0, 15970, 10870) - BB(0, 0, 320, 0),
        PlotterType.HP_7550A_A4: BB(0, 0, 10870, 7600) - BB(0, 0, 0, 320),
        # subtracting 8 mm of extra space from bottom. how much padding does this have on paper?

        PlotterType.HP_7475A_A4: BB(0, 0, 11040, 7721),
        PlotterType.HP_7475A_A3: BB(0, 0, 16158, 11040),

        PlotterType.HP_7470A_A4: BB(0, 0, 10900, 7650),

        PlotterType.HP_DM_RX_PLUS_A0: BB(-21760, -15400, 22880, 15480),
        PlotterType.HP_DM_RX_PLUS_100x70cm: BB(-19230, -13791, 19230, 13791),
        PlotterType.HP_DM_RX_PLUS_A1: BB(-16090, -11684, 16090, 11684),
        PlotterType.HP_DM_RX_PLUS_A2: BB(-10740, -8230, 10740, 8230),
        PlotterType.HP_DM_RX_PLUS_A3: BB(-7302, -5820, 7302, 5820),

        PlotterType.HP_DM_SX_A1: BB(-16100, -11600, 16100, 11600),
        PlotterType.HP_DM_SX_A3: BB(-7690, -5744, 7690, 5744),

        PlotterType.HP_DM_II_A1: BB(-16080, -11660, 16080, 11660),
        PlotterType.HP_DM_II_A3: BB(-7656, -5740, 7656, 5740),

        PlotterType.MUTOH_XP500_100x70cm: BB(-19370, -13728, 19370, 13728),
        PlotterType.MUTOH_XP500_500x297mm: BB(-9452, -5722, 9452, 5722),
        PlotterType.MUTOH_XP500_A1: BB(-16200, -11645, 16200, 11645),
        PlotterType.MUTOH_XP500_A2: BB(-11284, -8149, 11285, 8149),
        PlotterType.MUTOH_XP500_A3: BB(-7815, -5716, 7815, 5716),

        PlotterType.DIY_PLOTTER: BB(0, 0, 3350, -1715),
        PlotterType.AXIDRAW: BB(0, 0, 0, 0),  # todo: missing real bounds

        PlotterType.ROLAND_DXY1200_A3: BB(0, 0, 16158, 11040),
        PlotterType.ROLAND_DXY1200_A3_EXPANDED: BB(0, 0, 17272, 11880),
        PlotterType.ROLAND_DXY980: BB(0, 0, 16158, 11040),
        # PlotterType.HP_7595A_A0: BB(-23160, -17602, 23160 + 1160, 17602),
        # HP_7595A: minimum 35mm padding
        PlotterType.ROLAND_PNC1000: BB(0, 0, 18800, 40000),  # actually unlimited y
        PlotterType.ROLAND_PNC1000_50x100: BB(260, 560, 18700, 39000),  # for 50x100cm paper centered
        PlotterType.TEKTRONIX_4662: BB(0, 0, 4095, 2731),
        # tekronix: 10x15 inches (25.4 x 38.1 cm)

        PlotterType.DIGIPLOT_A1: BB(0, 0, 33600, 23700),

        PlotterType.HP_7570A_A1: BB(-16134, -11663, 16134, 11663),
    }


class PlotterName:
    # please create configurations like this
    # https://djipco.github.io/hpgl/hpgl.js.html
    names = {
        PlotterType.ROLAND_DPX3300_A1: "dpx3300_a1",
        PlotterType.ROLAND_DPX3300_A2: "dpx3300_a2",
        PlotterType.ROLAND_DPX3300_A3: "dpx3300_a3",

        PlotterType.HP_7550A_A3: "hp7550a_a3",
        PlotterType.HP_7550A_A4: "hp7550a_a4",

        PlotterType.HP_7475A_A3: "hp7475a_a3",
        PlotterType.HP_7475A_A4: "hp7475a_a4",

        PlotterType.HP_7470A_A4: "hp7470a_a4",

        PlotterType.HP_DM_RX_PLUS_A0: "hpdm_rx_plus_a0",
        PlotterType.HP_DM_RX_PLUS_100x70cm: "hpdm_rx_plus_100x70cm",
        PlotterType.HP_DM_RX_PLUS_A1: "hpdm_rx_plus_a1",
        PlotterType.HP_DM_RX_PLUS_A2: "hpdm_rx_plus_a2",
        PlotterType.HP_DM_RX_PLUS_A3: "hpdm_rx_plus_a3",

        PlotterType.HP_DM_II_A1: "hpdm_ii_a1",
        PlotterType.HP_DM_II_A3: "hpdm_ii_a3",

        PlotterType.HP_DM_SX_A1: "hpdm_sx_a1",
        PlotterType.HP_DM_SX_A3: "hpdm_sx_a3",

        PlotterType.MUTOH_XP500_100x70cm: "mutoh_xp500_100x70cm",
        PlotterType.MUTOH_XP500_500x297mm: "mutoh_xp500_500x297mm",
        PlotterType.MUTOH_XP500_A1: "mutoh_xp500_a1",
        PlotterType.MUTOH_XP500_A2: "mutoh_xp500_a2",
        PlotterType.MUTOH_XP500_A3: "mutoh_xp500_a3",

        PlotterType.AXIDRAW: "axidraw",
        PlotterType.DIY_PLOTTER: "custom",
        PlotterType.ROLAND_DXY1200_A3: "dxy1200",
        PlotterType.ROLAND_DXY980: "dxy980",
        PlotterType.ROLAND_PNC1000: "roland_camm1",
        PlotterType.TEKTRONIX_4662: "tektronix4662",

        PlotterType.DIGIPLOT_A1: "digiplot_a1",
        PlotterType.ROLAND_PNC1000_50x100: "roland_pnc1000",

        PlotterType.HP_7570A_A1: "hp7570a_draftpro",
    }


class PlotterHpglNames:
    names = {
        "DPX-3300": [PlotterType.ROLAND_DPX3300_A1, PlotterType.ROLAND_DPX3300_A2, PlotterType.ROLAND_DPX3300_A3],
        "7550A": [PlotterType.HP_7550A_A3, PlotterType.HP_7550A_A4],
        "7475A": [PlotterType.HP_7475A_A3, PlotterType.HP_7475A_A4],
        "7595A": [PlotterType.HP_DM_SX_A1, PlotterType.HP_DM_SX_A3, PlotterType.MUTOH_XP500_100x70cm,
                  PlotterType.MUTOH_XP500_500x297mm,
                  PlotterType.MUTOH_XP500_A1, PlotterType.MUTOH_XP500_A2, PlotterType.MUTOH_XP500_A3],
        "7596A": [PlotterType.HP_DM_II_A1, PlotterType.HP_DM_II_A3, PlotterType.HP_DM_RX_PLUS_A0,
                  PlotterType.HP_DM_RX_PLUS_100x70cm, PlotterType.HP_DM_RX_PLUS_A1, PlotterType.HP_DM_RX_PLUS_A2,
                  PlotterType.HP_DM_RX_PLUS_A3],

        "DXY-1200": [PlotterType.ROLAND_DXY1200_A3],
        "DXY-980": [PlotterType.ROLAND_DXY980],

        "7470A": [PlotterType.HP_7470A_A4],
        "7570A": [PlotterType.HP_7570A_A1],
    }


class XYFactors:
    fac = {
        PlotterType.ROLAND_DPX3300_A1: (40, 40),
        PlotterType.ROLAND_DPX3300_A2: (40, 40),
        PlotterType.ROLAND_DPX3300_A3: (40, 40),

        PlotterType.HP_7550A_A3: (40, 40),
        PlotterType.HP_7550A_A4: (40, 40),

        PlotterType.DIY_PLOTTER: (2.85714, 2.90572),
        PlotterType.AXIDRAW: (3.704, 3.704),
        PlotterType.HP_7475A_A3: (40, 40),
        PlotterType.HP_7475A_A4: (40, 40),
        PlotterType.ROLAND_DXY1200_A3: (40, 40),
        PlotterType.ROLAND_DXY980: (40, 40),
        PlotterType.HP_DM_RX_PLUS_A1: (40, 40),
        PlotterType.ROLAND_PNC1000: (40, 40),
        PlotterType.HP_DM_RX_PLUS_A3: (37, 37),
        PlotterType.TEKTRONIX_4662: (9.75, 9.19525),
        PlotterType.HP_DM_II_A1: (39.948, 40),
        PlotterType.HP_DM_II_A3: (39.948, 40),
        PlotterType.DIGIPLOT_A1: (40, 40),
        PlotterType.HP_7470A_A4: (40, 40),
        PlotterType.HP_DM_RX_PLUS_A2: (40, 39.5),
        PlotterType.ROLAND_PNC1000_50x100: (40.04, 40.04),
        PlotterType.HP_DM_RX_PLUS_A0: (39.9, 40.04),
        PlotterType.HP_DM_RX_PLUS_100x70cm: (40.0, 40.0),
        PlotterType.HP_DM_SX_A1: (40.0, 40.0),
        PlotterType.HP_DM_SX_A3: (40.0, 40.0),
        PlotterType.HP_7570A_A1: (40.0, 40.0),
        PlotterType.MUTOH_XP500_100x70cm: (40.0, 40.0),
        PlotterType.MUTOH_XP500_500x297mm: (40.0, 40.0),
        PlotterType.MUTOH_XP500_A1: (40.0, 40.0),
        PlotterType.MUTOH_XP500_A2: (40.0, 40.0),
        PlotterType.MUTOH_XP500_A3: (40.0, 40.0),
    }


class MaxSpeed:
    fac = {
        PlotterType.ROLAND_DPX3300_A1: 40,
        PlotterType.ROLAND_DPX3300_A2: 40,
        PlotterType.ROLAND_DPX3300_A3: 40,

        PlotterType.HP_7550A_A3: 80,
        PlotterType.HP_7550A_A4: 80,

        PlotterType.DIY_PLOTTER: 1,
        PlotterType.AXIDRAW: 1,
        PlotterType.HP_7475A_A3: 40,
        PlotterType.HP_7475A_A4: 40,
        PlotterType.ROLAND_DXY1200_A3: 40,
        PlotterType.ROLAND_DXY980: 40,
        PlotterType.HP_DM_RX_PLUS_A1: 110,
        PlotterType.ROLAND_PNC1000: 40,
        PlotterType.HP_DM_RX_PLUS_A3: 40,
        PlotterType.TEKTRONIX_4662: 1,
        PlotterType.HP_DM_II_A1: 110,
        PlotterType.HP_DM_II_A3: 110,
        PlotterType.DIGIPLOT_A1: 1,
        PlotterType.HP_7470A_A4: 40,
        PlotterType.HP_DM_RX_PLUS_A2: 110,
        PlotterType.ROLAND_PNC1000_50x100: 40,
        PlotterType.HP_DM_RX_PLUS_A0: 110,
        PlotterType.HP_DM_RX_PLUS_100x70cm: 110,
        PlotterType.HP_DM_SX_A1: 110,
        PlotterType.HP_DM_SX_A3: 110,
        PlotterType.MUTOH_XP500_100x70cm: 110,
        PlotterType.MUTOH_XP500_500x297mm: 110,
        PlotterType.MUTOH_XP500_A1: 110,
        PlotterType.MUTOH_XP500_A2: 110,
        PlotterType.MUTOH_XP500_A3: 110,
        PlotterType.HP_7570A_A1: 80,
    }


class BufferSize:
    # Default buffer sizes. Can be changed
    fac = {
        PlotterType.ROLAND_DPX3300_A1: 0,  # 0 = not tested
        PlotterType.ROLAND_DPX3300_A2: 0,
        PlotterType.ROLAND_DPX3300_A3: 0,

        PlotterType.HP_7550A_A3: 512,
        PlotterType.HP_7550A_A4: 512,

        PlotterType.DIY_PLOTTER: 1,
        PlotterType.AXIDRAW: 1,
        PlotterType.HP_7475A_A3: 512,
        PlotterType.HP_7475A_A4: 512,
        PlotterType.ROLAND_DXY1200_A3: 0,
        PlotterType.ROLAND_DXY980: 0,
        PlotterType.HP_DM_RX_PLUS_A1: 1024,
        PlotterType.ROLAND_PNC1000: 0,
        PlotterType.HP_DM_RX_PLUS_A3: 1024,
        PlotterType.TEKTRONIX_4662: 0,
        PlotterType.HP_DM_II_A1: 1024,
        PlotterType.HP_DM_II_A3: 1024,
        PlotterType.DIGIPLOT_A1: 0,
        PlotterType.HP_7470A_A4: 256,
        PlotterType.HP_DM_RX_PLUS_A2: 1024,
        PlotterType.ROLAND_PNC1000_50x100: 0,
        PlotterType.HP_DM_RX_PLUS_A0: 1024,
        PlotterType.HP_DM_RX_PLUS_100x70cm: 1024,
        PlotterType.HP_7570A_A1: 512,
        PlotterType.HP_DM_SX_A1: 1024,
        PlotterType.MUTOH_XP500_100x70cm: 1024,
        PlotterType.MUTOH_XP500_500x297mm: 1024,
        PlotterType.MUTOH_XP500_A1: 1024,
        PlotterType.MUTOH_XP500_A2: 1024,
        PlotterType.MUTOH_XP500_A3: 1024,
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
        PaperSize.PHOTO_PAPER_240_178_LANDSCAPE: "photo_paper_240x178",
        PaperSize.PHOTO_PAPER_250_200_LANDSCAPE: "photo_paper_250x200",
        PaperSize.PHOTO_PAPER_400_300_LANDSCAPE: "photo_paper_400x300",
        PaperSize.PHOTO_PAPER_600_500_LANDSCAPE: "photo_paper_600x500",
    }


class Paper:
    sizes = {
        PaperSize.PORTRAIT_36_48: BB(0, 0, 360, 480),
        PaperSize.LANDSCAPE_48_36: BB(0, 0, 480, 360),
        PaperSize.PORTRAIT_42_56: BB(0, 0, 420, 560),
        PaperSize.LANDSCAPE_56_42: BB(0, 0, 560, 420),
        PaperSize.PORTRAIT_50_70: BB(0, 0, 500, 700),
        PaperSize.LANDSCAPE_70_50: BB(0, 0, 700, 500),
        PaperSize.SQUARE_70_70: BB(0, 0, 700, 700),
        PaperSize.PORTRAIT_70_100: BB(0, 0, 700, 1000),
        PaperSize.LANDSCAPE_100_70: BB(0, 0, 1000, 700),
        PaperSize.LANDSCAPE_A4: BB(0, 0, 297, 210),
        PaperSize.PORTRAIT_A4: BB(0, 0, 210, 297),
        PaperSize.LANDSCAPE_A1: BB(0, 0, 841, 594),
        PaperSize.LANDSCAPE_A0: BB(0, 0, 1119, 771),
        PaperSize.PORTRAIT_A3: BB(0, 0, 297, 420),
        PaperSize.LANDSCAPE_A3: BB(0, 0, 420, 297),
        PaperSize.LANDSCAPE_80_50: BB(0, 0, 800, 500),
        PaperSize.PORTRAIT_50_80: BB(0, 0, 500, 800),
        PaperSize.LANDSCAPE_A2: BB(0, 0, 594, 420),
        PaperSize.SQUARE_59_59: BB(0, 0, 590, 590),
        PaperSize.SQUARE_25_25: BB(0, 0, 215, 170),
        PaperSize.LANDSCAPE_A1_HP_7596B: BB(0, 0, 776, 555),
        PaperSize.PORTRAIT_50_100: BB(0, 0, 460, 960),
        PaperSize.PHOTO_PAPER_240_178_LANDSCAPE: BB(0, 0, 240, 178),
        PaperSize.PHOTO_PAPER_250_200_LANDSCAPE: BB(0, 0, 250, 200),
        PaperSize.PHOTO_PAPER_400_300_LANDSCAPE: BB(0, 0, 400, 300),
        PaperSize.PHOTO_PAPER_600_500_LANDSCAPE: BB(0, 0, 600, 500),
    }
