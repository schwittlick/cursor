from cursor.path import PathCollection
from cursor.path import Path
from cursor.path import BoundingBox

import svgwrite
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
    def __init__(self, paths):
        assert isinstance(paths, PathCollection), "Only PathCollection objects allowed"
        self.paths = paths

    def points(self):
        for p in self.paths:
            for point in p.vertices:
                yield point

    def connections(self):
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
    def __init__(self, folder):
        assert isinstance(folder, pathlib.Path), "Only path objects allowed"
        self.save_path = folder
        self.dwg = None
        self.paths = PathCollection()
        self.bbs = []

    def render(self, paths):
        if not isinstance(paths, PathCollection):
            raise Exception("Only PathCollection and list of PathCollections allowed")

        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        # for path in paths:
        #    log.good(f"with {len(path)} verts")
        self.paths += paths

    def render_bb(self, bb):
        assert isinstance(bb, BoundingBox), "Only BoundingBox objects allowed"

        self.bbs.append(bb)

        p1 = Path()
        p1.add(bb.x, bb.y)
        p1.add(bb.w, bb.y)
        p1.add(bb.w, bb.h)
        p1.add(bb.x, bb.h)
        p1.add(bb.x, bb.y)

        self.paths.add(p1)

    def save(self, filename: str):
        bb = self.paths.bb()

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path / (filename + ".svg")
        self.dwg = svgwrite.Drawing(
            fname.as_posix(), profile="tiny", size=(bb.w + bb.x, bb.h + bb.y)
        )

        it = PathIterator(self.paths)
        for conn in it.connections():
            start = conn[0]
            end = conn[1]

            self.dwg.add(
                self.dwg.line(
                    start.pos(),
                    end.pos(),
                    stroke_width=0.5,
                    stroke=svgwrite.rgb(0, 0, 0, "%"),
                )
            )

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        log.good(f"Finished saving {fname}")

        self.dwg.save()


class GCodeRenderer:
    def __init__(
        self,
        folder,
        feedrate_xy=2000,
        feedrate_z=1000,
        z_down=3.5,
        z_up=0.0,
        invert_y=True,
    ):
        assert isinstance(folder, pathlib.Path), "Only path objects allowed"

        self.save_path = folder
        self.z_down = z_down
        self.z_up = z_up
        self.feedrate_xy = feedrate_xy
        self.feedrate_z = feedrate_z
        self.invert_y = invert_y
        self.paths = PathCollection()
        self.bbs = []

    def render(self, paths):
        if not isinstance(paths, PathCollection):
            raise Exception("Only PathCollection and list of PathCollections allowed")

        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        # for path in paths:
        #    log.good(f"with {len(path)} verts")
        self.paths += paths

    def render_bb(self, bb):
        assert isinstance(bb, BoundingBox), "Only BoundingBox objects allowed"
        self.bbs.append(bb)

    def save(self, filename: str):
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
                    _w = bb.w
                    _h = bb.h
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

    def __append_to_file(self, file, x, y):
        # if y < DrawingMachine.Plotter.MAX_Y:
        #    raise DrawingOutOfBoundsException(y)
        # if x > DrawingMachine.Plotter.MAX_X:
        #    raise DrawingOutOfBoundsException(x)
        file.write(f"G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n")


class RealtimeRenderer:
    def __init__(self):
        pass

    def render_pc(self, app, _pc):
        it = PathIterator(_pc)

        for conn in it.connections():
            start = conn[0]
            end = conn[1]

            app.line(start.x, start.y, end.x, end.y)

    def render(self, paths):
        from processing_py import App

        app = App(1920, 1080)  # create window: width, height

        t = 0
        while t < 500:
            print(f"frame {t}")
            t += 1
            app.background(0, 0, 0)  # set background:  red, green, blue
            app.fill(255, 255, 0)  # set color for objects: red, green, blue
            app.ellipse(
                app.mouseX, app.mouseY, 50, 50
            )  # draw a circle: center_x, center_y, size_x, size_y
            app.fill(255, 255, 255)
            # app.textFont("JetBrains Mono", 100)
            # app.text(str(t), 100, 100)
            app.stroke(255, 255, 255)
            self.render_pc(app, paths)
            app.redraw()  # refresh the window
        app.exit()


class HPGLRenderer:
    def __init__(
        self,
        folder: pathlib.Path,
        speed: int = 30,
        layer_pen_mapping: dict = None,
        linetype_mapping: dict = None,
    ) -> None:
        self.save_path = folder
        self.paths = PathCollection()
        self.layer_pen_mapping = layer_pen_mapping
        self.linetype_mapping = linetype_mapping

    def render(self, paths: "PathCollection") -> None:
        self.paths += paths
        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")

    def save(self, filename: str) -> None:
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
        fname = self.save_path / (filename + ".hpgl")

        with open(fname.as_posix(), "w") as file:
            # file.write(f"PA0,0;\n")
            file.write("SP1;\n")

            self.__append_to_file(file, 0.0, 0.0)

            first = True
            for p in self.paths:

                if first:
                    file.write("PU;\n")
                    first = False
                x = p.start_pos().x
                y = p.start_pos().y

                file.write(f"SP{self.__pen_from_layer(p.layer)};\n")
                file.write(f"LT{self.__linetype_from_layer(p.line_type)};\n")
                file.write(f"VS{self.__get_velocity(p.velocity)};\n")

                self.__append_to_file(file, x, y)
                file.write("PD;\n")
                for line in p.vertices:
                    x = line.x
                    y = line.y
                    self.__append_to_file(file, x, y)
                file.write("PU;\n")

            self.__append_to_file(file, 0.0, 0.0)
            file.write("SP0;\n")
        log.good(f"Finished saving {fname}")

    @staticmethod
    def __append_to_file(file, x: float, y: float):
        file.write(f"PA{int(x)},{int(y)}\n")

    def __pen_from_layer(self, layer: str) -> int:
        if self.layer_pen_mapping is None:
            return 1

        if layer not in self.layer_pen_mapping.keys():
            return 1

        return self.layer_pen_mapping[layer]

    def __linetype_from_layer(self, linetype: int) -> str:
        _default_linetype = ""
        if self.linetype_mapping is None:
            return _default_linetype

        if linetype not in self.linetype_mapping.keys():
            return _default_linetype

        return self.linetype_mapping[linetype]

    @staticmethod
    def __get_velocity(velocity: int) -> int:
        if velocity is None:
            return 45

        return velocity


class JpegRenderer:
    def __init__(self, folder: pathlib.Path):
        self.save_path = folder
        self.img = None
        self.img_draw = None

    def render(self, paths, scale=1.0, frame=False, thickness=1):
        if not isinstance(paths, PathCollection):
            raise Exception("Only PathCollection allowed")

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

        image_width = int(abs_scaled_bb[0] + abs_scaled_bb[2])
        image_height = int(abs_scaled_bb[1] + abs_scaled_bb[3])

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

    def save(self, filename: str):
        fname = self.save_path / (filename + ".jpg")
        self.img.save(fname, "JPEG")
        log.good(f"Finished saving {fname}")

    def render_bb(self, bb):
        assert isinstance(bb, BoundingBox), "Only BoundingBox objects allowed"

        self.img_draw.line(xy=(bb.x, bb.y, bb.w, bb.y), fill="black", width=2)
        self.img_draw.line(xy=(bb.x, bb.y, bb.x, bb.h), fill="black", width=2)
        self.img_draw.line(xy=(bb.w, bb.y, bb.w, bb.h), fill="black", width=2)
        self.img_draw.line(xy=(bb.x, bb.h, bb.w, bb.h), fill="black", width=2)

    def render_frame(self):
        w = self.img.size[0]
        h = self.img.size[1]
        self.img_draw.line(xy=(0, 0, w, 0), fill="black", width=2)
        self.img_draw.line(xy=(0, 0, 0, h), fill="black", width=2)
        self.img_draw.line(xy=(w - 2, 0, w - 2, h), fill="black", width=2)
        self.img_draw.line(xy=(0, h - 2, w, h - 2), fill="black", width=2)


class AsciiRenderer:
    def __init__(self, folder: pathlib.Path, jpeg_renderer: JpegRenderer):
        self.save_path = folder
        self.jpeg_renderer = jpeg_renderer
        self.pixels = " .,:;i1tfLCG08#"
        self.output = ""

    def get_raw_char(self, r: int, g: int, b: int, a: int):
        value = r  # self.intensity(r, g, b, a)
        precision = 255 / (len(self.pixels) - 1)
        rawChar = self.pixels[int(round(value / precision))]

        return rawChar

    @staticmethod
    def intensity(r: int, g: int, b: int, a: int):
        return (r + g + b) * a

    def render(self, paths, scale=1.0, frame=False, thickness=1):
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

    def save(self, filename: str):
        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
        fname = self.save_path / (filename + ".txt")
        with open(fname.as_posix(), "w") as file:
            file.write(self.output)
        log.good(f"Finished saving {fname}")
