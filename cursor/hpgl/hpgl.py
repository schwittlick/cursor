from __future__ import annotations

import logging
import math
from dataclasses import replace

from cursor.hpgl import CR, LB_TERMINATOR, LF
from cursor.hpgl.metrics import (
    DEFAULT_LABEL_ORIGIN,
    DEFAULT_PLOTTER_UNIT,
    LABEL_ORIGINS,
    MAX_LABEL_LENGTH,
    FontMetrics,
    label_origin_offset,
    rotate,
)


class HPGL:
    def __init__(self):
        self.plotter_unit = DEFAULT_PLOTTER_UNIT
        self.__data: list[str] = []

        self.__reset()

    def __reset(self) -> None:
        """The state a plotter comes up in, and returns to on IN."""
        self.terminator = LB_TERMINATOR
        self.pos = (0, 0)
        self.metrics = FontMetrics.default(self.plotter_unit)
        self.degree = 0
        self.label_origin = DEFAULT_LABEL_ORIGIN

    @property
    def data(self) -> str:
        return "".join(self.__data)

    def save(self, fn: str) -> None:
        logging.info(f"Saving {fn}")
        with open(fn, "w", encoding="utf-8") as file:
            file.write(self.data)

    def custom(self, data: str) -> None:
        """
        Use with caution, positions  could be impacted
        """
        self.__data.append(data)

    def IN(self) -> None:
        self.__data.append("IN;")

        self.__reset()

    def SP(self, pen: int) -> None:
        self.__data.append(f"SP{pen};")

    def VS(self, speed: int) -> None:
        self.__data.append(f"VS{speed};")

    def FS(self, force: int) -> None:
        self.__data.append(f"FS{force};")

    def LT(self, line_type: tuple[int, int]) -> None:
        self.__data.append(f"LT{line_type[0]},{line_type[1]};")

    def DT(self, c: chr = chr(3)):
        self.terminator = c
        self.__data.append(f"DT{c};")

    def IW(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.__data.append(f"IW{x1},{y1},{x2},{y2};")

    def PA(self, x: int, y: int) -> None:
        self.__data.append(f"PA{int(x)},{int(y)};")
        self.pos = (x, y)

    def PD(self, x: int = None, y: int = None) -> None:
        if x is None or y is None:
            self.__data.append("PD;")
        else:
            self.__data.append(f"PD{int(x)},{int(y)};")
            self.pos = (x, y)

    def PU(self, x: int = None, y: int = None) -> None:
        if x is None or y is None:
            self.__data.append("PU;")
        else:
            self.__data.append(f"PU{int(x)},{int(y)};")
            self.pos = (x, y)

    # LABEL STUFF

    def LB(self, label: str) -> None:
        """
        Plot a label, and track where it leaves the pen.

        A label may carry its own line breaks: chr(13) is CR, returning to the column the
        label started in, and chr(10) is LF, dropping one line. So a two line label reads
        f"LBline1{chr(13)}{chr(10)}line2{chr(3)}".
        """
        if len(label) == 0:
            logging.warning("Empty Label, discarding")
            return

        if len(label) > MAX_LABEL_LENGTH:
            logging.warning(f"Label too long: {len(label)} > {MAX_LABEL_LENGTH}")
            logging.warning(label)

        self.__data.append(f"LB{label}{self.terminator}")

        self.pos = self.label_end(label)

    def label_width(self, label: str) -> float:
        """The widest line of a label, in plotter units."""
        widest = run = 0
        for char in label:
            run = 0 if char in (CR, LF) else run + 1
            widest = max(widest, run)

        return widest * self.metrics.advance_x

    def label_end(self, label: str) -> tuple[float, float]:
        """
        Where the pen ends up after plotting label from the current position.

        Worked out in the text's own frame -- along the baseline, dropping a line per LF
        -- and then turned by DI, so it holds for rotated text too.
        """
        origin_x, origin_y = label_origin_offset(self.label_origin, self.label_width(label), self.metrics)

        x, y = origin_x, origin_y
        for char in label:
            if char == CR:
                x = origin_x
            elif char == LF:
                y -= self.metrics.line_height
            else:
                x += self.metrics.advance_x

        return rotate(self.pos, (self.pos[0] + x, self.pos[1] + y), math.radians(self.degree))

    def SL(self, degree: float) -> None:
        if degree <= -90 or degree >= 90:
            raise ValueError(f"Slant is too high: {degree} should be within -90 and 90")
        slant = math.tan(degree * (math.pi / 180))
        self.__data.append(f"SL{slant:.3f};")

    def DI(self, degree: float) -> None:
        self.degree = degree
        run = math.cos(degree * (math.pi / 180))
        rise = math.sin(degree * (math.pi / 180))
        self.__data.append(f"DI{run:.3f},{rise:.3f};")

    def SI(self, x_cm: float, y_cm: float) -> None:
        """
        Sets the font size in cm.

        Defaults are (set when SI is executed without parameters)
        A3: 0.285, 0.375
        A4: 0.187, 0.269
        """
        self.metrics = replace(self.metrics, char_width_cm=x_cm, char_height_cm=y_cm)
        self.__data.append(f"SI{x_cm:.3f},{y_cm:.3f};")

    def ES(self, spaces: float = 0, line: float = 0) -> None:
        """
        Extra space between characters and lines, as a fraction of the character cell.

        Negative values tighten the setting. The cell is 1.5x the character wide, so
        -0.33 is roughly where neighbouring glyphs start to touch.
        """
        self.metrics = replace(self.metrics, extra_space=spaces, extra_line=line)
        self.__data.append(f"ES{spaces:.3f},{line:.3f};")

    def LO(self, lo: int = DEFAULT_LABEL_ORIGIN):
        """
        Label Origin, where the label sits relative to the point it is plotted at.

        1: left bottom (default)
        2: left center
        3: left top
        4: center bottom
        5: center center
        6: center top
        7: right bottom
        8: right center
        9: right top
        11-19: as 1-9, with half a character of clearance from the point
        """
        if lo not in LABEL_ORIGINS:
            raise ValueError(f"LO; must be one of {LABEL_ORIGINS}. Used={lo}")

        self.label_origin = lo
        self.__data.append(f"LO{lo};")

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
