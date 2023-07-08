from __future__ import annotations

import math

import wasabi

log = wasabi.Printer()


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class HPGL:
    def __init__(self):
        self._terminator = chr(3)
        self.plotter_unit = 40
        self.pos = (0, 0)
        self.char_size = (40, 40)

        self.char_spacing = 1.5
        self.line_spacing = 2.0
        self.degree = 0

        self.data = ""

    def save(self, fn):
        with open(fn, "w", encoding='utf-8') as file:
            file.write(self.data)

    def custom(self, hpgl: HPGL) -> None:
        """
        Use with caution, positions positions could be impacted
        """
        self.data += hpgl.data

    def config_memory(self, io: int = 1024, polygon: int = 1778, char: int = 0, replot: int = 9954, vector: int = 44):
        max_memory_hp7550 = 12800

        assert 2 <= io <= 12752
        assert 4 <= polygon <= 12754
        assert 0 <= char <= 12750
        assert 0 <= replot <= 12750
        assert 44 <= vector <= 12794
        assert sum([io, polygon, char, replot, vector]) < max_memory_hp7550

        ESC = chr(27)
        ESC_TERM = ":"
        buffer_sizes = f"{ESC}.T{io};{polygon};{char};{replot};{vector}{ESC_TERM}"
        wait = f"{ESC}.L"  # returns io buffer size when its empty. read it and wait for reply several seconds
        logical_buffer_size = f"{ESC}.@{io}{ESC_TERM}"

    def IN(self) -> None:
        self.data += f"IN;"

        self._terminator = chr(3)
        self.pos = (0, 0)
        self.char_size = (40, 40)

        self.char_spacing = 1.5
        self.line_spacing = 2.0
        self.degree = 0

    def SP(self, pen: int) -> None:
        self.data += f"SP{pen};"

    def VS(self, speed: int) -> None:
        self.data += f"VS{speed};"

    def DT(self, c: chr = chr(3)):
        self._terminator = c
        self.data += f"DT{c};"

    def IW(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.data += f"IW{x1},{y1},{x2},{y2};"

    def PA(self, x: int, y: int) -> None:
        self.data += f"PA{x},{y};"
        self.pos = (x, y)

    def PD(self, x: int = None, y: int = None) -> None:
        assert x and y
        assert not x and not y

        if not x or not y:
            self.data += "PD;"
        else:
            self.data += f"PD{x},{y};"
            self.pos = (x, y)

    def PU(self, x: int = None, y: int = None) -> None:
        assert x and y
        assert not x and not y

        if not x or not y:
            self.data += "PU;"
        else:
            self.data += f"PU{x},{y};"
            self.pos = (x, y)

    # LABEL STUFF

    def LB(self, label: str) -> None:
        """
        todo:
        chr(10) is LF (line feed), moves control point down 1 line from current pos
        chr(13) is CR (carriage return), moves the carriage return point (control point when LB command was encountered)
        e.g. to make a new line within a LB statement: f"LBline1{chr(13)}{chr(10)}line2{chr(3)}"
        """
        if len(label) == 0:
            log.warn(f"Empty Label, discarding")
            return

        if len(label) > 150:
            log.warn(f"Label too long: {len(label)} > 150")

        self.data += f"LB{label}{self._terminator}"

        assert chr(10) is not in label or chr(13) is not in label
        # for now the internal LF/CR commands are not being calculated
        new_x = len(label) * self.char_size[0] * self.char_spacing
        new_y = 0
        self.pos = rotate(self.pos, (new_x, new_y), math.radians(self.degree))

    def SL(self, degree: float) -> None:
        if degree < -90 or degree > 90:
            log.warn(f"Slant is too high: {degree} should be within -90 and 90")
        slant = math.tan(degree * (math.pi / 180))
        self.data += f"SL{slant:.3f};"

    def DI(self, degree: float) -> None:
        self.degree = degree
        rise = math.cos(degree)
        run = math.sin(degree)
        self.data += f"DI{run:.3f},{rise:.3f};"

    def DV(self, dir: int = 0):
        """
        direction vertical
        0: horizontal (default)
        1: vertical
        """
        assert dir == 0 or dir == 1
        self.data += f"DV{dir};"

    def SI(self, x: float, y: float) -> None:
        """
        Sets the font size in cm.

        Defaults are (set when SI is executed without parameters)
        A3: 0.285, 0.375
        A4: 0.187, 0.269
        """
        self.char_size = (x * self.plotter_unit, y * self.plotter_unit)
        self.data += f"SI{x:.3f},{y:.3f};"

    def ES(self, spaces: float, line: float) -> None:
        self.char_spacing = spaces
        self.line_spacing = line
        self.data += f"ES{spaces:.3f},{line:.3f};"

    def LO(self, lo):
        """
        Label Origin
        1: left bottom (default)
        2: left center
        3: left top
        4: center bottom
        5: center center
        6: center top
        7: right bottom
        8: right center
        9: right top
        10-19: half char width/height offset
        """
        assert lo != 10

        self.data += f"LO{lo};"

    def SR(self):
        # size relative (to P1/P2 points)
        pass

    def DR(self):
        # direction relative
        pass

    def CP(self):
        # character plot
        # without parameter does CR+LF
        pass

    def BL(self:):
        # buffered label
        pass

    def OL(self):
        # output label length instruction
        pass
