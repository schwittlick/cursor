from __future__ import annotations

import copy
import os
import pathlib
import random
import typing

import arcade
import pymsgbox
import svgwrite
import wasabi
from PIL import Image, ImageDraw
from arcade.experimental.uislider import UISlider
from arcade.gui import UIManager, UIOnChangeEvent, UIAnchorWidget

from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.data import DataDirHandler, DateHandler
from cursor.hpgl.hpgl import HPGL
from cursor.path import Path
from cursor.position import Position

log = wasabi.Printer()


class DrawingOutOfBoundsException(Exception):
    """
    Raised when trying to generate gcode that exceeds the drawing machine dimensions
    """

    pass


class PathIterator:
    def __init__(self, paths: Collection):
        self.paths = paths

    def points(self) -> typing.Iterator[Position]:
        for p in self.paths:
            for point in p.vertices:
                yield point

    def connections(
            self,
    ) -> typing.Iterator[typing.Tuple[Position, Position]]:
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
        self.paths = Collection()
        self.bbs = []

    def render(self, paths: Collection) -> None:
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def render_bb(self, bb: BoundingBox) -> None:
        self.bbs.append(bb)

        p1 = Path()
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
                conn[0].as_tuple(),
                conn[1].as_tuple(),
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
        self.paths = Collection()

    def render(self, paths: Collection) -> None:
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def g01(self, x: float, y: float, z: float) -> str:
        return f"G01 X{x:.2f} Y{y:.2f} Z{z:.2f} F{self.feedrate_xy}"

    def generate_instructions(self) -> list[str]:
        instructions = []
        instructions.append(self.g01(0, 0, self.z_up))
        for p in self.paths:
            x = p.start_pos().x
            y = p.start_pos().y
            z = self.z_down
            if self.invert_y:
                y = -y
            instructions.append(self.g01(x, y, self.z_up))

            if p.laser_volt:
                instructions.append(f"VOLT{p.laser_volt:.3}")

            if p.laser_delay:
                instructions.append(f"DELAY{p.laser_delay:.3}")

            if p.laser_amp:
                instructions.append(f"AMP{p.laser_amp:.3}")

            if "z" in self.paths[0].properties:
                z = self.paths[0].properties["z"]

            instructions.append(self.g01(x, y, z))

            if "laser" in p.properties:
                instructions.append("LASERON")

            for point in p.vertices:
                x = point.x
                y = point.y
                if self.invert_y:
                    y = -y
                z = self.z_down

                if "amp" in point.properties.keys():
                    amp = point.properties["amp"]
                    instructions.append(f"AMP{amp:.3}")
                if "volt" in point.properties.keys():
                    volt = point.properties["volt"]
                    instructions.append(f"VOLT{volt:.3}")
                if "z" in point.properties.keys():
                    z = point.properties["z"]

                instructions.append(self.g01(x, y, z))

            if "laser" in p.properties:
                instructions.append("LASEROFF")

            instructions.append(self.g01(x, y, self.z_up))

        return instructions

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
        fname = self.save_path / (filename + ".nc")
        instructions = self.generate_instructions()

        with open(fname.as_posix(), "w") as file:
            for instruction in instructions:
                file.write(f"{instruction}\n")
        log.good(f"Finished saving {fname}")


class RealtimeRenderer(arcade.Window):
    def screenshot(self, renderer: RealtimeRenderer):
        folder = DataDirHandler().jpg(f"{renderer.title}")
        suffix = pymsgbox.prompt("suffix", default="")
        fn = folder / f"{DateHandler().utc_timestamp()}_{suffix}.png"
        folder.mkdir(parents=True, exist_ok=True)
        log.good(f"saving {fn.as_posix()}")
        try:
            arcade.get_image(0, 0, self.width * 2, self.height * 2).save(fn.as_posix(), "PNG")
        except ValueError:
            pass
        except OSError:
            pass
        finally:
            pass

    def enter_fullscreen(self, rr: RealtimeRenderer):
        rr.set_fullscreen(not rr.fullscreen)

    def toggle_gui(self, rr: RealtimeRenderer):
        self._draw_gui = not self._draw_gui

    def __init__(self, width, height, title):
        super().__init__(width=width, height=height, title=title, samples=16)
        arcade.set_background_color(arcade.color.GRAY)
        self.__title = title
        self.colors = [
            (color, getattr(arcade.color, color))
            for color in dir(arcade.color)
            if not color.startswith("__")
        ]

        self.shapes = None
        self.collection = Collection()
        self.clear_list()

        self.cbs = {}
        self.pressed = {}
        self.long_press = {}
        self._on_mouse = None
        self._draw_gui = True

        self.add_cb(arcade.key.S, self.screenshot, False)
        self.add_cb(arcade.key.F, self.enter_fullscreen, False)
        self.add_cb(arcade.key.G, self.toggle_gui, False)

        self.background = None

        self.manager = UIManager()
        self.manager.enable()

        self.camera = arcade.Camera(width, height)

    def set_bg(self, p: pathlib.Path):
        self.background = arcade.load_texture(p)

    def add_slider(self):
        ui_slider = UISlider(value=50, width=300, height=50)

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            print(ui_slider.value)
            # label.text = f"{ui_slider.value:02.0f}"
            # label.fit_content()

        self.manager.add(UIAnchorWidget(child=ui_slider))

    def set_bg_color(self, col: arcade.color = None):
        if col:
            arcade.set_background_color(col)
        else:
            arcade.set_background_color(random.choice(self.colors)[1])

    @staticmethod
    def run():
        arcade.enable_timings(100)
        arcade.run()

    @property
    def title(self):
        return self.__title

    def set_on_mouse_cb(self, cb: typing.Callable):
        self._on_mouse = cb

    def add_cb(self, key: arcade.key, cb: typing.Callable, long_press: bool = True):
        self.cbs[key] = cb
        self.pressed[key] = False
        self.long_press[key] = long_press

    def clear_list(self):
        self.shapes = arcade.ShapeElementList()
        self.collection = Collection()

    def add_point(self, po: Position, width: int = 5, color: arcade.color = None):
        if not color:
            color = random.choice(self.colors)[1]
        _x = po.x
        _y = self.height - po.y
        point = arcade.create_ellipse(_x, _y, width, width, color)
        self.shapes.append(point)

    def add_path(self, p: Path, line_width: float = 5, color: arcade.color = None):
        if not color:
            color = random.choice(self.colors)[1]

        line_strip = arcade.create_line_strip(p.as_tuple_list(), color, line_width)
        self.shapes.append(line_strip)
        self.collection.add(p)

    def add_polygon(self, p: Path, color: arcade.color = None):
        # assert p.is_closed()
        if not color:
            color = random.choice(self.colors)[1]

        self.shapes.append(arcade.create_polygon(p.as_tuple_list(), color))

    def add_collection(
            self, c: Collection, line_width: float = 5, color: arcade.color = None
    ):
        if not color:
            color = random.choice(self.colors)[1]
        [self.add_path(p, line_width, color) for p in c]

    def on_draw(self):
        self.clear()

        self.camera.use()

        if self.background:
            arcade.draw_lrwh_rectangle_textured(0, 0, self.width, self.height, self.background)

        self.shapes.draw()
        if self._draw_gui:
            self.manager.draw()

    def on_update(self, delta_time: float):
        super().update(delta_time)

        fps = int(arcade.get_fps())
        caption = f"{self.__title} fps: {fps} shapes: {len(self.shapes)}"
        self.set_caption(caption)

        for k, v in self.pressed.items():
            if v:
                self.cbs[k](self)
                if not self.long_press[k]:
                    self.pressed[k] = False

    def on_key_press(self, key: int, modifiers: int):
        if key == arcade.key.ESCAPE:
            arcade.exit()
        elif key == arcade.key.C:
            self.clear_list()

        for k, v in self.cbs.items():
            if key == k:
                self.pressed[k] = True

    def on_key_release(self, key: int, modifiers: int):
        for k, v in self.cbs.items():
            if key == k:
                self.pressed[k] = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self._on_mouse:
            self._on_mouse(self, x, y, dx, dy)


class HPGLRenderer:
    def __init__(
            self,
            folder: pathlib.Path,
            layer_pen_mapping: dict = None,
            line_type_mapping: dict = None,
    ) -> None:
        self.__save_path = folder
        self.__paths = Collection()
        self.__layer_pen_mapping = layer_pen_mapping
        self.__line_type_mapping = line_type_mapping

    def render(self, paths: Collection) -> None:
        self.__paths += paths
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")

    def estimated_duration(self, speed) -> int:
        s = 0
        for p in self.__paths:
            mm = p.distance / 400  # for hp plotters its 40
            seconds = mm / speed * 10
            s += seconds
        return s

    def generate_string(self):
        _hpgl = HPGL()

        # _prev_line_type = 0
        _prev_velocity = 0
        _prev_force = 0
        _prev_pen = 0

        first = True
        for p in self.__paths:
            if first:
                _hpgl.PU()
                first = False
            x = p.start_pos().x
            y = p.start_pos().y

            if _prev_pen != p.pen_select:
                _hpgl.SP(self.__get_pen_select(p.pen_select))
                _prev_pen = p.pen_select

            # if p.line_type:
            #     if _prev_line_type != p.line_type:
            #         _hpgl_string += f"LT{self.__linetype_from_layer(p.line_type)};"
            #         _prev_line_type = p.line_type

            if p.velocity:
                if _prev_velocity != p.velocity:
                    _hpgl.VS(self.__get_velocity(p.velocity))
                    _prev_velocity = p.velocity

            if p.pen_force:
                if _prev_force != p.pen_force:
                    _hpgl.FS(self.__get_pen_force(p.pen_force))
                    _prev_force = p.pen_force

            if p.laser_pwm:
                _hpgl.custom(f"PWM{p.laser_pwm};")

            if p.laser_volt:
                _hpgl.custom(f"VOLT{p.laser_volt:.3};")

            if p.laser_delay:
                _hpgl.custom(f"DELAY{p.laser_delay:.3};")

            if p.laser_amp:
                _hpgl.custom(f"AMP{p.laser_amp:.3};")

            _hpgl.PA(x, y)
            if p.is_polygon:
                _hpgl.custom("PM0;")

            _hpgl.PD()

            for point in p.vertices:
                x = point.x
                y = point.y

                _hpgl.PA(x, y)

            _hpgl.PU()

            if p.is_polygon:
                _hpgl.custom("PM2;")  # switch to PM2; to close and safe
                _hpgl.custom("FP;")

        _hpgl.PA(0, 0)
        _hpgl.SP(0)

        return _hpgl.data

    def save(self, filename: str) -> str:
        pathlib.Path(self.__save_path).mkdir(parents=True, exist_ok=True)
        fname = self.__save_path / (filename + ".hpgl")

        _hpgl_string = self.generate_string()

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
        self.__paths = Collection()

        self.PEN_DOWN = "I;"
        self.PEN_UP = "H;"
        self.GO_ABSOLUTE = "K;"

    def render(self, paths: Collection) -> None:
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
    def __init__(self, folder: pathlib.Path, w: int = 1920, h: int = 1080):
        self.save_path = folder
        self.img = None
        self.img_draw = None

        self.image_width = w
        self.image_height = h

    def render(
            self,
            paths: Collection,
            scale: float = 1.0,
            frame: bool = False,
            thickness: int = 1,
    ) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        log.good(f"Creating image with size=({self.image_width}, {self.image_height})")
        assert self.image_width < 21000 and self.image_height < 21000, "keep resolution lower"

        self.img = Image.new("RGB", (self.image_width, self.image_height), "white")
        self.img_draw = ImageDraw.ImageDraw(self.img)

        it = PathIterator(paths)

        for conn in it.connections():
            start = conn[0]
            end = conn[1]

            self.img_draw.line(
                xy=(
                    start.x * scale, self.image_height - start.y * scale, end.x * scale,
                    self.image_height - end.y * scale),
                fill="black",
                width=thickness,
            )

        if frame:
            self.render_frame()

    def save(self, filename: str) -> None:
        fname = self.save_path / (filename + ".jpg")
        self.img.save(fname, "JPEG")
        log.good(f"Finished saving {fname}")

    def image(self) -> Image:
        return self.img

    def render_bb(self, bb: BoundingBox) -> None:
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
            paths: Collection,
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
