from cursor.path import PathCollection
from cursor.path import Path
from cursor.path import BoundingBox
from cursor.device import DrawingMachine
from cursor.device import RolandDPX3300

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

    def save(self, filename):
        bb = self.paths.bb()

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path.joinpath(filename + ".svg")
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

    def save(self, filename):
        try:
            pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
            fname = self.save_path.joinpath(filename + ".nc")
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
        if y < DrawingMachine.Plotter.MAX_Y:
            raise DrawingOutOfBoundsException(y)
        if x > DrawingMachine.Plotter.MAX_X:
            raise DrawingOutOfBoundsException(x)
        file.write(f"G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n")


class HPGLRenderer:
    def __init__(self, folder):
        assert isinstance(folder, pathlib.Path), "Only path objects allowed"

        self.save_path = folder
        self.paths = PathCollection()

    def render(self, paths):
        if not isinstance(paths, PathCollection):
            raise Exception("Only PathCollection and list of PathCollections allowed")

        log.good(f"{__class__.__name__}: rendered {len(paths)} paths")
        self.paths += paths

    def save(self, filename):
        try:
            pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)
            fname = self.save_path.joinpath(filename + ".hpgl")

            with open(fname.as_posix(), "w") as file:
                #file.write(f"PA0,0;\n")
                file.write(f"SP1;\n")
                self.__append_to_file(file, 0.0, 0.0)
                for p in self.paths:
                    x = p.start_pos().x
                    y = p.start_pos().y
                    self.__append_to_file(file, x, y)
                    file.write(f"PD;\n")
                    for line in p.vertices:
                        x = line.x
                        y = line.y
                        self.__append_to_file(file, x, y)
                    file.write(f"PU;\n")

                self.__append_to_file(file, 0.0, 0.0)
                file.write(f"SP0;\n")
            log.good(f"Finished saving {fname}")
        except DrawingOutOfBoundsException as e:
            log.fail(f"Couldn't generate GCode- Out of Bounds with position {e}")

    def __append_to_file(self, file, x, y):
        if y < RolandDPX3300.Plotter.MIN_Y:
            raise DrawingOutOfBoundsException(y)
        if y > RolandDPX3300.Plotter.MAX_Y:
            raise DrawingOutOfBoundsException(y)
        if x < RolandDPX3300.Plotter.MIN_X:
            raise DrawingOutOfBoundsException(x)
        if x > RolandDPX3300.Plotter.MAX_X:
            raise DrawingOutOfBoundsException(x)
        file.write(f"PA{int(x)},{int(y)}\n")

class JpegRenderer:
    def __init__(self, folder):
        assert isinstance(folder, pathlib.Path), "Only path objects allowed"
        self.save_path = folder
        self.img = None
        self.img_draw = None

    def render(self, paths, scale=1.0, frame=False):
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
        assert image_width < 20000 and image_height < 20000, "keep resolution lower"

        self.img = Image.new("RGB", (image_width, image_height,), "white",)
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
                width=1,
            )

        if frame:
            self.render_frame()

    def save(self, filename):
        fname = self.save_path.joinpath(filename + ".jpg")
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
