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
        self.terminator = chr(3)
        self.plotter_unit = 40
        self.pos = (0, 0)
        self.char_size_mm = (2.85, 3.75)

        self.char_spacing = 1.5
        self.line_spacing = 2.0
        self.degree = 0

        self.data = ""

    def save(self, fn):
        with open(fn, "w", encoding='utf-8') as file:
            file.write(self.data)

    def custom(self, data: str) -> None:
        """
        Use with caution, positions  could be impacted
        """
        self.data += data

    def IN(self) -> None:
        self.data += "IN;"

        self.terminator = chr(3)
        self.pos = (0, 0)
        self.char_size_mm = (2.85, 3.75)

        self.char_spacing = 1.5
        self.line_spacing = 2.0
        self.degree = 0

    def SP(self, pen: int) -> None:
        self.data += f"SP{pen};"

    def VS(self, speed: int) -> None:
        self.data += f"VS{speed};"

    def FS(self, force: int) -> None:
        self.data += f"FS{force};"

    def DT(self, c: chr = chr(3)):
        self.terminator = c
        self.data += f"DT{c};"

    def IW(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.data += f"IW{x1},{y1},{x2},{y2};"

    def PA(self, x: int, y: int) -> None:
        self.data += f"PA{int(x)},{int(y)};"
        self.pos = (x, y)

    def PD(self, x: int = None, y: int = None) -> None:
        if x is None or y is None:
            self.data += "PD;"
        else:
            self.data += f"PD{int(x)},{int(y)};"
            self.pos = (x, y)

    def PU(self, x: int = None, y: int = None) -> None:
        if x is None or y is None:
            self.data += "PU;"
        else:
            self.data += f"PU{int(x)},{int(y)};"
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
            log.warn("Empty Label, discarding")
            return

        if len(label) > 150:
            log.warn(f"Label too long: {len(label)} > 150")
            log.warn(label)

        self.data += f"LB{label}{self.terminator}"

        assert chr(10) not in label or chr(13) not in label
        # for now the internal LF/CR commands are not being calculated

        new_x = self.pos[0] + len(label) * self.char_size_mm[0] * self.plotter_unit * self.char_spacing
        new_y = self.pos[1]
        self.pos = rotate(self.pos, (new_x, new_y), math.radians(self.degree))

    def SL(self, degree: float) -> None:
        if degree <= -90 or degree >= 90:
            raise ValueError(f"Slant is too high: {degree} should be within -90 and 90")
        slant = math.tan(degree * (math.pi / 180))
        self.data += f"SL{slant:.3f};"

    def DI(self, degree: float) -> None:
        self.degree = degree
        run = math.cos(degree * (math.pi / 180))
        rise = math.sin(degree * (math.pi / 180))
        self.data += f"DI{run:.3f},{rise:.3f};"

    def SI(self, x_cm: float, y_cm: float) -> None:
        """
        Sets the font size in cm.

        Defaults are (set when SI is executed without parameters)
        A3: 0.285, 0.375
        A4: 0.187, 0.269
        """
        self.char_size_mm = (x_cm * 10, y_cm * 10)
        self.data += f"SI{x_cm:.3f},{y_cm:.3f};"

    def ES(self, spaces: float = 0, line: float = 0) -> None:
        self.char_spacing = spaces
        self.line_spacing = line
        self.data += f"ES{spaces:.3f},{line:.3f};"

    def LO(self, lo: int = 1):
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
        if lo == 10 or lo <= 0 or lo >= 20:
            raise ValueError(f"LO; may not be 10 or <=0 or >= 20. Used={lo}")

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

    def BL(self):
        # buffered label
        pass

    def OL(self):
        # output label length instruction
        pass
