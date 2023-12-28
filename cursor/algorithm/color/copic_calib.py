from cursor.algorithm.color.copic import CopicColor
from cursor.algorithm.color.copic_pen_enum import CopicColorCode


class CopicPhotograph:
    """
    These are manually added rgb colors taken from a photograph/scan calibration
    all pens have ben drawn on a piece of paper, in order to calibrate their differences
    """

    def __init__(self):
        self.colors = {}

        self.colors[CopicColorCode.Y06] = CopicColor(CopicColorCode.Y06, 'Yellow', (251, 238, 130))
        self.colors[CopicColorCode.YG21] = CopicColor(CopicColorCode.YG21, 'Anise', (227, 227, 170))
        self.colors[CopicColorCode.Y13] = CopicColor(CopicColorCode.Y13, 'Lemon Yellow', (248, 232, 153))
        self.colors[CopicColorCode.Y17] = CopicColor(CopicColorCode.Y17, 'Golden Yellow', (250, 189, 109))

        self.colors[CopicColorCode.YR24] = CopicColor(CopicColorCode.YR24, 'Pale Sepia', (166, 124, 104))
        self.colors[CopicColorCode.E37] = CopicColor(CopicColorCode.E37, 'Sepia', (192, 112, 85))
        self.colors[CopicColorCode.E39] = CopicColor(CopicColorCode.E39, 'Leather', (182, 99, 81))

        self.colors[CopicColorCode.RV13] = CopicColor(CopicColorCode.RV13, 'Tender Pink', (242, 185, 202))
        self.colors[CopicColorCode.RV09] = CopicColor(CopicColorCode.RV09, 'Fuchsia', (118, 96, 154))
        self.colors[CopicColorCode.R17] = CopicColor(CopicColorCode.R17, 'Lipstick Orange', (198, 77, 108))
        self.colors[CopicColorCode.YR07] = CopicColor(CopicColorCode.YR07, 'Cadmium Orange', (224, 99, 105))
        self.colors[CopicColorCode.R29] = CopicColor(CopicColorCode.R29, 'Lipstick Red', (222, 57, 108))

        self.colors[CopicColorCode.V12] = CopicColor(CopicColorCode.V12, 'Pale Lilac', (222, 204, 222))

        self.colors[CopicColorCode.G02] = CopicColor(CopicColorCode.G02, 'Spectrum Green', (155, 222, 175))
        self.colors[CopicColorCode.G14] = CopicColor(CopicColorCode.G14, 'Apple Green', (181, 221, 124))
        self.colors[CopicColorCode.G07] = CopicColor(CopicColorCode.G07, 'Nile Green', (92, 147, 92))
        self.colors[CopicColorCode.YG67] = CopicColor(CopicColorCode.YG67, 'Moss', (140, 164, 108))
        self.colors[CopicColorCode.G29] = CopicColor(CopicColorCode.G29, 'Pine Tree Green', (84, 125, 101))
        self.colors[CopicColorCode.G17] = CopicColor(CopicColorCode.G17, 'Forest Green', (60, 169, 116))
        self.colors[CopicColorCode.BG18] = CopicColor(CopicColorCode.BG18, 'Teal Blue', (121, 182, 181))

        self.colors[CopicColorCode.B12] = CopicColor(CopicColorCode.B12, 'Ice Blue', (73, 116, 182))
        self.colors[CopicColorCode.B24] = CopicColor(CopicColorCode.B24, 'Sky', (106, 180, 192))
        self.colors[CopicColorCode.B39] = CopicColor(CopicColorCode.B39, 'Prussian Blue', (71, 110, 160))

        self.colors[CopicColorCode._110] = CopicColor(CopicColorCode._110, 'Special Black', (75, 67, 74))

        self.colors[CopicColorCode.E97] = CopicColor(CopicColorCode.E97, 'Deep Orange', (246, 170, 116))
        self.colors[CopicColorCode.G40] = CopicColor(CopicColorCode.G40, 'Dim Green', (246, 246, 224))
        self.colors[CopicColorCode.YG01] = CopicColor(CopicColorCode.YG01, 'Green Bice', (223, 240, 89))
        self.colors[CopicColorCode.R20] = CopicColor(CopicColorCode.R20, 'Blush', (245, 198, 202))
        self.colors[CopicColorCode.YR04] = CopicColor(CopicColorCode.YR04, 'Chrome Orange', (248, 127, 87))
        self.colors[CopicColorCode.YR02] = CopicColor(CopicColorCode.YR02, 'Light Orange', (242, 145, 155))

        self.colors[CopicColorCode.E04] = CopicColor(CopicColorCode.E04, 'Lipstick Rose', (211, 150, 167))
        self.colors[CopicColorCode.G03] = CopicColor(CopicColorCode.G03, 'Maedow Green', (137, 218, 148))
        self.colors[CopicColorCode.BG09] = CopicColor(CopicColorCode.BG09, 'Blue Green', (41, 167, 168))
        self.colors[CopicColorCode.BG13] = CopicColor(CopicColorCode.BG13, 'Mint Green', (116, 217, 203))
        self.colors[CopicColorCode.BG15] = CopicColor(CopicColorCode.BG15, 'Aqua', (85, 212, 192))
        self.colors[CopicColorCode.G85] = CopicColor(CopicColorCode.G85, 'Verdigris', (165, 175, 134))
