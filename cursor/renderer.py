import cursor.path
import cursor.bb

import svgwrite
import os
import typing
import sys
import pathlib
import wasabi
import copy
from PIL import Image, ImageDraw

log = wasabi.Printer()


class DrawingOutOfBoundsException(Exception):
    """
    Raised when trying to generate gcode that exceeds the drawing machine dimensions
    """

    pass


class PathIterator:
    def __init__(self, paths: "cursor.collection.Collection"):
        self.paths = paths

    def points(self) -> typing.Iterator["cursor.path.Position"]:
        for p in self.paths:
            for point in p.vertices:
                yield point

    def connections(
        self,
    ) -> typing.Iterator[typing.Tuple["cursor.path.Position", "cursor.path.Position"]]:
        prev = None

        for p in self.paths:
            is_first_vertex = True
            for point in p:
                if is_first_vertex:
                    prev = copy.deepcopy(point)
                    is_first_vertex = False

                    continue

                start = prev
                end = copy.deepcopy(point)
                prev = copy.deepcopy(point)

                yield start, end


class SvgRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path = folder
        self.dwg = None
        self.paths = cursor.collection.Collection()
        self.bbs = []

    def render(self, paths: "cursor.collection.Collection") -> None:
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def render_bb(self, bb: "cursor.bb.BoundingBox") -> None:
        self.bbs.append(bb)

        p1 = cursor.path.Path()
        p1.add(bb.x, bb.y)
        p1.add(bb.x2, bb.y)
        p1.add(bb.x2, bb.y2)
        p1.add(bb.x, bb.y2)
        p1.add(bb.x, bb.y)

        self.paths.add(p1)

    def save(self, filename: str) -> None:
        bb = self.paths.bb()

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".svg")
        self.dwg = svgwrite.Drawing(fname.as_posix(), profile="tiny", size=(bb.w, bb.h))

        it = PathIterator(self.paths)
        for conn in it.connections():
            line = self.dwg.line(
                conn[0].astuple(),
                conn[1].astuple(),
                stroke_width=0.5,
                stroke="black",
            )
            self.dwg.add(line)

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        log.good(f"Finished saving {fname}")

        self.dwg.save()


class GCodeRenderer:
    def __init__(
        self,
        folder: pathlib.Path,
        feedrate_xy: int = 2000,
        feedrate_z: int = 1000,
        z_down: float = 3.5,
        z_up: float = 0.0,
        invert_y: bool = True,
    ):
        self.save_path = folder
        self.z_down = z_down
        self.z_up = z_up
        self.feedrate_xy = feedrate_xy
        self.feedrate_z = feedrate_z
        self.invert_y = invert_y
        self.paths = cursor.collection.Collection()
        self.bbs = []

    def render(self, paths: "cursor.collection.Collection") -> None:
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def render_bb(self, bb: "cursor.bb.BoundingBox") -> None:
        self.bbs.append(bb)

    def save(self, filename: str) -> None:
        try:
            pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
            fname = self.save_path / (filename + ".nc")
            with open(fname.as_posix(), "w") as file:
                file.write(f"G01 Z0.0 F{self.feedrate_z}\n")
                self.__append_to_file(file, 0.0, 0.0)
                for p in self.paths:
                    x = p.start_pos().x
                    y = p.start_pos().y
                    if self.invert_y:
                        y = -y
                    self.__append_to_file(file, x, y)
                    file.write(f"G01 Z{self.z_down} F{self.feedrate_z}\n")
                    for line in p.vertices:
                        x = line.x
                        y = line.y
                        if self.invert_y:
                            y = -y
                        self.__append_to_file(file, x, y)
                    file.write(f"G01 Z{self.z_up} F{self.feedrate_z}\n")

                for bb in self.bbs:
                    _x = bb.x
                    _y = bb.y
                    if self.invert_y:
                        _y = -_y
                    _w = bb.x2
                    _h = bb.y2
                    if self.invert_y:
                        _h = -_h
                    file.write(f"G01 Z0.0 F{self.feedrate_z}\n")
                    self.__append_to_file(file, _x, _y)
                    file.write(f"G01 Z{self.z_down} F{self.feedrate_z}\n")
                    self.__append_to_file(file, _x, _h)
                    self.__append_to_file(file, _w, _h)
                    self.__append_to_file(file, _w, _y)
                    self.__append_to_file(file, _x, _y)

                file.write(f"G01 Z0.0 F{self.feedrate_z}\n")
                self.__append_to_file(file, 0.0, 0.0)
            log.good(f"Finished saving {fname}")
        except DrawingOutOfBoundsException as e:
            log.fail(f"Couldn't generate GCode- Out of Bounds with position {e}")

    def __append_to_file(self, file: typing.TextIO, x: float, y: float) -> None:
        file.write(f"G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n")


class RealtimeRenderer:
    def __init__(self, w: int, h: int):
        self.running = False
        self.__cbs = []
        self.w = w
        self.h = h
        self.pcs = []
        self.selected = 0

    def set_cb(self, key: str, cb: typing.Callable, reset: bool = False) -> None:
        self.__cbs.append((ord(key), cb, reset))

    def _pygameinit(self) -> None:
        import pygame

        pygame.init()
        self.screen = pygame.display.set_mode((self.w, self.h))

        self.screen.fill((255, 255, 255))
        pygame.display.update()
        self.running = True

    def _line(
        self, screen, p1: "cursor.path.Position", p2: "cursor.path.Position"
    ) -> None:
        import pygame

        pygame.draw.line(screen, (0, 0, 0), p1.astuple(), p2.astuple())

    def add(self, pc: "cursor.collection.Collection") -> None:
        self.pcs.append(pc)

    def set(self, pcs: typing.List["cursor.collection.Collection"]) -> None:
        self.pcs = pcs
        self.selected = 0

    def render(self) -> None:
        import pygame

        if len(self.pcs) == 0:
            log.fail("No paths to render. Quitting")
            return

        self._pygameinit()

        frame_count = 0
        while self.running:
            pygame.display.set_caption(f"selected {self.selected}")
            self.screen.fill((255, 255, 255))
            it = PathIterator(self.pcs[self.selected])
            ev = pygame.event.get()
            for conn in it.connections():
                start = conn[0]
                end = conn[1]
                self._line(self.screen, start, end)
            pygame.display.update()

            if frame_count % 60 == 0:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_LEFT] and pressed[pygame.K_LCTRL]:
                    self.selected -= 1
                    if self.selected < 0:
                        self.selected = len(self.pcs) - 1

                if pressed[pygame.K_RIGHT] and pressed[pygame.K_LCTRL]:
                    self.selected += 1
                    if self.selected >= len(self.pcs):
                        self.selected = 0

                for cbk in self.__cbs:
                    if pressed[cbk[0]] and pressed[pygame.K_LCTRL]:
                        cbk[1](self.selected, self.pcs[self.selected])
                        if cbk[2]:
                            self.selected = 0

            frame_count += 1
            for event in ev:
                if event.type == pygame.MOUSEBUTTONUP:
                    pygame.display.update()
                if event.type == pygame.KEYDOWN:
                    for cbk in self.__cbs:
                        if cbk[0] == event.key:
                            cbk[1](self.selected, self.pcs[self.selected])
                    # if event.key == pygame.K_s:
                    #    if self.cb:
                    #        self.cb(self.selected, self.pcs[self.selected])
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        pygame.quit()
                        sys.exit(0)

                    if event.key == pygame.K_LEFT:
                        self.selected -= 1
                        if self.selected < 0:
                            self.selected = len(self.pcs) - 1
                    if event.key == pygame.K_RIGHT:
                        self.selected += 1
                        if self.selected >= len(self.pcs):
                            self.selected = 0

                if event.type == pygame.QUIT:
                    self.running = False


class HPGLRenderer:
    def __init__(
        self,
        folder: pathlib.Path,
        layer_pen_mapping: dict = None,
        line_type_mapping: dict = None,
    ) -> None:
        self.__save_path = folder
        self.__paths = cursor.collection.Collection()
        self.__layer_pen_mapping = layer_pen_mapping
        self.__line_type_mapping = line_type_mapping

    def render(self, paths: "cursor.collection.Collection") -> None:
        self.__paths += paths
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".hpgl")

        _hpgl_string = ""

        _hpgl_string += "SP1;\n"
        _hpgl_string += "PA0,0\n"

        first = True
        for p in self.__paths:
            if first:
                _hpgl_string += "PU;\n"
                first = False
            x = p.start_pos().x
            y = p.start_pos().y

            _hpgl_string += f"SP{self.__get_pen_select(p.pen_select)};\n"
            _hpgl_string += f"LT{self.__linetype_from_layer(p.line_type)};\n"

            if p.velocity:
                _hpgl_string += f"VS{self.__get_velocity(p.velocity)};\n"

            if p.pen_force:
                _hpgl_string += f"FS{self.__get_pen_force(p.pen_force)};\n"

            _hpgl_string += f"PA{int(x)},{int(y)};\n"
            if p.is_polygon:
                _hpgl_string += "PM0;\n"

            _hpgl_string += "PD;\n"

            for line in p.vertices:
                x = line.x
                y = line.y
                _hpgl_string += f"PA{int(x)},{int(y)};\n"

            _hpgl_string += "PU;\n"

            if p.is_polygon:
                _hpgl_string += "PM2;\n"  # switch to PM2; to close and safe
                _hpgl_string += "FP;\n"

        _hpgl_string += "PA0,0;\n"
        _hpgl_string += "SP0;\n"

        with open(fname.as_posix(), "w") as file:
            file.write(_hpgl_string)

        log.good(f"Finished saving {fname}")

        return _hpgl_string

    @staticmethod
    def __get_pen_select(pen_select: typing.Optional[int] = None) -> int:
        if pen_select is None:
            return 1

        return pen_select

    def __pen_from_layer(self, layer: typing.Optional[str] = None) -> int:
        if self.__layer_pen_mapping is None:
            return 1

        if layer not in self.__layer_pen_mapping.keys():
            return 1

        return self.__layer_pen_mapping[layer]

    def __linetype_from_layer(self, linetype: typing.Optional[int] = None) -> str:
        _default_linetype = ""
        if self.__line_type_mapping is None:
            return _default_linetype

        if linetype not in self.__line_type_mapping.keys():
            return _default_linetype

        return self.__line_type_mapping[linetype]

    @staticmethod
    def __get_velocity(velocity: typing.Optional[int] = None) -> int:
        if velocity is None:
            return 110

        return velocity

    @staticmethod
    def __get_pen_force(pen_force: typing.Optional[int] = None) -> int:
        if pen_force is None:
            return 16

        return pen_force


class TektronixRenderer:
    def __init__(
        self,
        folder: pathlib.Path,
    ):
        self.__save_path = folder
        self.__paths = cursor.collection.Collection()

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

    def render(self, paths: "cursor.collection.Collection") -> None:
        self.__paths += paths
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")

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

        log.good(f"Finished saving {fname}")

        return output_string


class DigiplotRenderer:
    def __init__(
        self,
        folder: pathlib.Path,
    ):
        self.__save_path = folder
        self.__paths = cursor.collection.Collection()

        self.PEN_DOWN = "I;"
        self.PEN_UP = "H;"
        self.GO_ABSOLUTE = "K;"

    def render(self, paths: "cursor.collection.Collection") -> None:
        self.__paths += paths
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")

    @staticmethod
    def _coord_string(x: int, y: int) -> str:
        return f"X,{x};/Y,{y};"  # coord + go absolute

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".digi")

        output_string = ""

        for p in self.__paths:
            x = int(p.start_pos().x)
            y = int(p.start_pos().y)
            output_string += self._coord_string(x, y)
            output_string += self.PEN_UP
            output_string += self.GO_ABSOLUTE
            for line in p.vertices:
                x = int(line.x)
                y = int(line.y)
                output_string += self._coord_string(x, y)
                output_string += self.PEN_DOWN
                output_string += self.GO_ABSOLUTE

        output_string += self._coord_string(0, 0)
        output_string += self.PEN_UP
        output_string += self.GO_ABSOLUTE

        with open(fname.as_posix(), "wb") as file:
            file.write(output_string.encode("utf-8"))

        log.good(f"Finished saving {fname}")

        return output_string


class JpegRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path = folder
        self.img = None
        self.img_draw = None

    def render(
        self,
        paths: "cursor.collection.Collection",
        scale: float = 1.0,
        frame: bool = False,
        thickness: int = 1,
    ) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        if len(paths) == 0:
            log.warn("Not creating image, empty paths")
            return

        bb = paths.bb()

        abs_scaled_bb = (
            abs(bb.x * scale),
            abs(bb.y * scale),
            abs(bb.w * scale),
            abs(bb.h * scale),
        )

        image_width = int(abs_scaled_bb[0] + abs_scaled_bb[2]) + int(bb.x * scale)
        image_height = int(abs_scaled_bb[1] + abs_scaled_bb[3]) + int(bb.y * scale)

        log.good(f"Creating image with size=({image_width}, {image_height})")
        assert image_width < 21000 and image_height < 21000, "keep resolution lower"

        self.img = Image.new("RGB", (image_width, image_height), "white")
        self.img_draw = ImageDraw.ImageDraw(self.img)

        it = PathIterator(paths)

        for conn in it.connections():
            start = conn[0]
            end = conn[1]

            # offset paths when passed bb starts in negative space
            if bb.x * scale < 0:
                start.x += abs_scaled_bb[0]
                end.x += abs_scaled_bb[0]

            if bb.y * scale < 0:
                start.y += abs_scaled_bb[1]
                end.y += abs_scaled_bb[1]

            self.img_draw.line(
                xy=(start.x * scale, start.y * scale, end.x * scale, end.y * scale),
                fill="black",
                width=thickness,
            )

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        fname = self.save_path / (filename + ".jpg")
        self.img.save(fname, "JPEG")
        log.good(f"Finished saving {fname}")

    def render_bb(self, bb: "cursor.bb.BoundingBox") -> None:
        self.img_draw.line(xy=(bb.x, bb.y, bb.x2, bb.y), fill="black", width=2)
        self.img_draw.line(xy=(bb.x, bb.y, bb.x, bb.y2), fill="black", width=2)
        self.img_draw.line(xy=(bb.x2, bb.y, bb.x2, bb.y2), fill="black", width=2)
        self.img_draw.line(xy=(bb.x, bb.y2, bb.x2, bb.y2), fill="black", width=2)

    def render_frame(self) -> None:
        w = self.img.size[0]
        h = self.img.size[1]
        self.img_draw.line(xy=(0, 0, w, 0), fill="black", width=2)
        self.img_draw.line(xy=(0, 0, 0, h), fill="black", width=2)
        self.img_draw.line(xy=(w - 2, 0, w - 2, h), fill="black", width=2)
        self.img_draw.line(xy=(0, h - 2, w, h - 2), fill="black", width=2)


class VideoRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path = folder
        self.images = []

    def add_frame(self, img) -> None:
        self.images.append(img)

    def render_video(self, fname: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        text_file = (self.save_path / "list.txt").as_posix()

        p = pathlib.Path(self.save_path.absolute()).glob("**/*.jpg")
        files = [x for x in p if x.is_file()]
        with open(text_file, "w", encoding="utf8") as file:
            for f in files:
                file.write("file '")
                file.write(f.as_posix().replace("/", "\\"))
                file.write("'")
                file.write("\n")

        out_file = self.save_path / fname
        call = (
            f'ffmpeg -y -r 25 -f concat -safe 0 -i "{text_file}" -c:v libx264 -vf '
            f'"fps=25,format=yuv420p,scale=trunc(iw/2)*2:trunc(ih/2)*2" {out_file}'
        )

        os.system(call)


class AsciiRenderer:
    def __init__(self, folder: pathlib.Path, jpeg_renderer: JpegRenderer):
        self.save_path = folder
        self.jpeg_renderer = jpeg_renderer
        self.pixels = " .,:;i1tfLCG08#"
        self.output = ""

    def get_raw_char(self, r: int, g: int, b: int, a: int) -> str:
        value = r  # self.intensity(r, g, b, a)
        precision = 255 / (len(self.pixels) - 1)
        rawChar = self.pixels[int(round(value / precision))]

        return rawChar

    @staticmethod
    def intensity(r: int, g: int, b: int, a: int) -> int:
        return (r + g + b) * a

    def render(
        self,
        paths: "cursor.collection.Collection",
        scale: float = 1.0,
        frame: bool = False,
        thickness: int = 1,
    ):
        self.jpeg_renderer.render(paths, scale, frame, thickness)

        im = self.jpeg_renderer.img

        columns = 100
        rows = 50

        im = im.resize((columns, rows))
        px = im.load()
        size = im.size
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                _px = px[x, y]
                _a = self.get_raw_char(_px[0], _px[1], _px[2], 1)
                self.output = self.output + _a
            self.output = self.output + "\n"

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
        fname = self.save_path / (filename + ".txt")
        with open(fname.as_posix(), "w") as file:
            file.write(self.output)
        log.good(f"Finished saving {fname}")
