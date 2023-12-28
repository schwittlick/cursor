from cursor.algorithm.color.copic import Color
from cursor.algorithm.color.copic_pen_enum import CopicColorCode


class CopicPhotograph:
    """
    These are manually added rgb colors taken from a photograph/scan calibration
    all pens have ben drawn on a piece of paper, in order to calibrate their differences
    """

    def __init__(self):
        self.colors = {}

        self.colors[CopicColorCode.Y06] = Color((251, 238, 130))
        self.colors[CopicColorCode.YG21] = Color((227, 227, 170))
        self.colors[CopicColorCode.Y13] = Color((248, 232, 153))
        self.colors[CopicColorCode.Y17] = Color((250, 189, 109))

        self.colors[CopicColorCode.YR24] = Color((166, 124, 104))
        self.colors[CopicColorCode.E37] = Color((192, 112, 85))
        self.colors[CopicColorCode.E39] = Color((182, 99, 81))

        self.colors[CopicColorCode.RV13] = Color((242, 185, 202))
        self.colors[CopicColorCode.RV09] = Color((118, 96, 154))
        self.colors[CopicColorCode.R17] = Color((198, 77, 108))
        self.colors[CopicColorCode.YR07] = Color((224, 99, 105))
        self.colors[CopicColorCode.R29] = Color((222, 57, 108))

        self.colors[CopicColorCode.V12] = Color((222, 204, 222))

        self.colors[CopicColorCode.G02] = Color((155, 222, 175))
        self.colors[CopicColorCode.G14] = Color((181, 221, 124))
        self.colors[CopicColorCode.G07] = Color((92, 147, 92))
        self.colors[CopicColorCode.YG67] = Color((140, 164, 108))
        self.colors[CopicColorCode.G29] = Color((84, 125, 101))
        self.colors[CopicColorCode.G17] = Color((60, 169, 116))
        self.colors[CopicColorCode.BG18] = Color((121, 182, 181))

        self.colors[CopicColorCode.B12] = Color((73, 116, 182))
        self.colors[CopicColorCode.B24] = Color((106, 180, 192))
        self.colors[CopicColorCode.B39] = Color((71, 110, 160))

        self.colors[CopicColorCode._110] = Color((75, 67, 74))

        self.colors[CopicColorCode.E97] = Color((246, 170, 116))
        self.colors[CopicColorCode.G40] = Color((246, 246, 224))
        self.colors[CopicColorCode.YG01] = Color((223, 240, 89))
        self.colors[CopicColorCode.R20] = Color((245, 198, 202))
        self.colors[CopicColorCode.YR04] = Color((248, 127, 87))
        self.colors[CopicColorCode.YR02] = Color((242, 145, 155))

        self.colors[CopicColorCode.E04] = Color((211, 150, 167))
        self.colors[CopicColorCode.G03] = Color((137, 218, 148))
        self.colors[CopicColorCode.BG09] = Color((41, 167, 168))
        self.colors[CopicColorCode.BG13] = Color((116, 217, 203))
        self.colors[CopicColorCode.BG15] = Color((85, 212, 192))
        self.colors[CopicColorCode.G85] = Color((165, 175, 134))
