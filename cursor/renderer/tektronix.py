from __future__ import annotations

import pathlib
import logging
from cursor.collection import Collection



class TektronixRenderer:
    def __init__(
            self,
            folder: pathlib.Path,
    ):
        self.__save_path = folder
        self.__paths = Collection()

    def _coords_to_bytes(self, xcoord: int, ycoord: int, low_res: bool = False) -> str:
        """
        Converts integer coordinates to the funky 12-bit byte coordinate
        codes expected by the Tek plotter in graph mode.
        returns a byte string:
        <HIGH Y><Remainders (low 2 bits added)><LOW Y><HIGH X><LOW X>

        all characters are offset so they are in the typable ascii range
        since they were designed for manual input on a 1970s tty/terminal keyboard
        """
        if low_res:
            eb = ""
        else:
            remx = xcoord % 4
            remy = ycoord % 4
            eb = chr(96 + remx + (4 * remy))  # see Operators manual Appendix B-1

        # the 'low' bits are actually the highest 5 of the lowest 7 bits
        # there is also a lower precision mode that ignores the remainder
        low_y = chr(96 + ((ycoord // 4) & 0b11111))
        low_x = chr(64 + ((xcoord // 4) & 0b11111))

        hi_y = chr(32 + (ycoord // 128))
        hi_x = chr(32 + (xcoord // 128))

        return hi_y + eb + low_y + hi_x + low_x

    def render(self, paths: Collection) -> None:
        self.__paths += paths
        logging.info(f"{__class__.__name__}: rendered {len(paths)} paths")

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".tek")

        GS = chr(29)
        ESC = chr(27)
        FF = chr(12)
        US = chr(31)
        # BEL = chr(7)

        # Escape + init? + Go-to-graph-mode
        output_string = ESC + "AE" + GS

        for p in self.__paths:
            x = int(p.start_pos().x)
            y = int(p.start_pos().y)
            output_string += self._coords_to_bytes(x, y)  # move, pen-up
            for line in p.vertices:
                x = int(line.x)
                y = int(line.y)
                output_string += self._coords_to_bytes(x, y)  # draw, pen-down

        # Escape + Move-to-home + Go-to-alpha-mode
        output_string += ESC + FF + US

        with open(fname.as_posix(), "wb") as file:
            file.write(output_string.encode("utf-8"))

        logging.info(f"Finished saving {fname}")

        return output_string
