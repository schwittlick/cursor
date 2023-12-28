from cursor.algorithm.color.copic import CopicColor
from cursor.algorithm.color.copic_pen_enum import CopicPen


class CopicPhotograph:
    """
    These are manually added rgb colors taken from a photograph/scan calibration
    all pens have ben drawn on a piece of paper, in order to calibrate their differences
    """

    def __init__(self):
        self.colors = {}

        self.colors[CopicPen.Y06] = CopicColor(CopicPen.Y06, 'Yellow', (251, 238, 130))
        self.colors[CopicPen.YG21] = CopicColor(CopicPen.YG21, 'Anise', (227, 227, 170))
        self.colors[CopicPen.Y13] = CopicColor(CopicPen.Y13, 'Lemon Yellow', (248, 232, 153))
        self.colors[CopicPen.Y17] = CopicColor(CopicPen.Y17, 'Golden Yellow', (250, 189, 109))

        self.colors[CopicPen.YR24] = CopicColor(CopicPen.YR24, 'Pale Sepia', (166, 124, 104))
        self.colors[CopicPen.E37] = CopicColor(CopicPen.E37, 'Sepia', (192, 112, 85))
        self.colors[CopicPen.E39] = CopicColor(CopicPen.E39, 'Leather', (182, 99, 81))

        self.colors[CopicPen.RV13] = CopicColor(CopicPen.RV13, 'Tender Pink', (242, 185, 202))
        self.colors[CopicPen.RV09] = CopicColor(CopicPen.RV09, 'Fuchsia', (118, 96, 154))
        self.colors[CopicPen.R17] = CopicColor(CopicPen.R17, 'Lipstick Orange', (198, 77, 108))
        self.colors[CopicPen.YR07] = CopicColor(CopicPen.YR07, 'Cadmium Orange', (224, 99, 105))
        self.colors[CopicPen.R29] = CopicColor(CopicPen.R29, 'Lipstick Red', (222, 57, 108))

        self.colors[CopicPen.V12] = CopicColor(CopicPen.V12, 'Pale Lilac', (222, 204, 222))

        self.colors[CopicPen.G02] = CopicColor(CopicPen.G02, 'Spectrum Green', (155, 222, 175))
        self.colors[CopicPen.G14] = CopicColor(CopicPen.G14, 'Apple Green', (181, 221, 124))
        self.colors[CopicPen.G07] = CopicColor(CopicPen.G07, 'Nile Green', (92, 147, 92))
        self.colors[CopicPen.YG67] = CopicColor(CopicPen.YG67, 'Moss', (140, 164, 108))
        self.colors[CopicPen.G29] = CopicColor(CopicPen.G29, 'Pine Tree Green', (84, 125, 101))
        self.colors[CopicPen.G17] = CopicColor(CopicPen.G17, 'Forest Green', (60, 169, 116))
        self.colors[CopicPen.BG18] = CopicColor(CopicPen.BG18, 'Teal Blue', (121, 182, 181))

        self.colors[CopicPen.B12] = CopicColor(CopicPen.B12, 'Ice Blue', (73, 116, 182))
        self.colors[CopicPen.B24] = CopicColor(CopicPen.B24, 'Sky', (106, 180, 192))
        self.colors[CopicPen.B39] = CopicColor(CopicPen.B39, 'Prussian Blue', (71, 110, 160))

        self.colors[CopicPen._110] = CopicColor(CopicPen._110, 'Special Black', (75, 67, 74))

        self.colors[CopicPen.E97] = CopicColor(CopicPen.E97, 'Deep Orange', (246, 170, 116))
        self.colors[CopicPen.G40] = CopicColor(CopicPen.G40, 'Dim Green', (246, 246, 224))
        self.colors[CopicPen.YG01] = CopicColor(CopicPen.YG01, 'Green Bice', (223, 240, 89))
        self.colors[CopicPen.R20] = CopicColor(CopicPen.R20, 'Blush', (245, 198, 202))
        self.colors[CopicPen.YR04] = CopicColor(CopicPen.YR04, 'Chrome Orange', (248, 127, 87))
        self.colors[CopicPen.YR02] = CopicColor(CopicPen.YR02, 'Light Orange', (242, 145, 155))

        self.colors[CopicPen.E04] = CopicColor(CopicPen.E04, 'Lipstick Rose', (211, 150, 167))
        self.colors[CopicPen.G03] = CopicColor(CopicPen.G03, 'Maedow Green', (137, 218, 148))
        self.colors[CopicPen.BG09] = CopicColor(CopicPen.BG09, 'Blue Green', (41, 167, 168))
        self.colors[CopicPen.BG13] = CopicColor(CopicPen.BG13, 'Mint Green', (116, 217, 203))
        self.colors[CopicPen.BG15] = CopicColor(CopicPen.BG15, 'Aqua', (85, 212, 192))
        self.colors[CopicPen.G85] = CopicColor(CopicPen.G85, 'Verdigris', (165, 175, 134))
