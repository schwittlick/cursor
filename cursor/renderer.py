from cursor import path

import svgwrite
import pathlib
from PIL import Image, ImageDraw


class PathIterator:
    def __init__(self, paths):
        self.paths = paths

    def points(self):
        for collection in self.paths:
            for p in collection:
                for point in p.vertices:
                    yield point, collection.resolution

    def connections(self, scaled=False):
        prev = None

        for collection in self.paths:
            for p in collection:
                is_first_vertex = True
                for point in p:
                    if is_first_vertex:
                        prev = point.copy()
                        is_first_vertex = False

                        continue

                    start = prev
                    end = point.copy()
                    prev = point.copy()

                    if scaled:
                        start.scale(
                            collection.resolution.width, collection.resolution.height
                        )
                        end.scale(
                            collection.resolution.width, collection.resolution.height
                        )

                    yield start, end


class CursorSVGRenderer:
    def __init__(self, folder):
        assert isinstance(folder, pathlib.Path), "Only path objects allowed"
        self.save_path = folder

    def render(self, paths, filename):
        if not isinstance(paths, path.PathCollection):
            raise Exception("Only PathCollection and list of PathCollections allowed")

        bb = paths.bb()

        fname = self.save_path.joinpath(filename + ".svg")
        dwg = svgwrite.Drawing(fname, profile="tiny", size=(bb.w + bb.x, bb.h + bb.y))

        it = PathIterator([paths])
        for conn in it.connections(scaled=False):
            start = conn[0]
            end = conn[1]

            dwg.add(
                dwg.line(
                    start.pos(),
                    end.pos(),
                    stroke_width=0.5,
                    stroke=svgwrite.rgb(0, 0, 0, "%"),
                )
            )

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        print(f"Saving to {fname}")
        dwg.save()


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

    def render(self, paths, filename):
        if not isinstance(paths, path.PathCollection):
            raise Exception("Only PathCollection and list of PathCollections allowed")

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        fname = self.save_path.joinpath(filename + ".nc")
        print(f"Saving to {fname}")
        with open(fname, "w") as file:
            file.write(f"G01 Z0.0 F{self.feedrate_z}\n")
            file.write(f"G01 X0.0 Y0.0 F{self.feedrate_xy}\n")
            for p in paths:
                x = p.start_pos().x
                y = p.start_pos().y
                if self.invert_y:
                    y = -y
                file.write(f"G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n")
                file.write(f"G01 Z{self.z_down} F{self.feedrate_z}\n")
                for line in p.vertices:
                    x = line.x
                    y = line.y
                    if self.invert_y:
                        y = -y
                    file.write(f"G01 X{x:.2f} Y{y:.2f} F{self.feedrate_xy}\n")
                file.write(f"G01 Z{self.z_up} F{self.feedrate_z}\n")
            file.write(f"G01 Z0.0 F{self.feedrate_z}\n")
            file.write(f"G01 X0.0 Y0.0 F{self.feedrate_xy}\n")


class JpegRenderer:
    def __init__(self, folder):
        assert isinstance(folder, pathlib.Path), "Only path objects allowed"
        self.save_path = folder

    def render(self, paths, filename, scale=1.0):
        if not isinstance(paths, path.PathCollection):
            raise Exception("Only PathCollection and list of PathCollections allowed")

        pathlib.Path(self.save_path).mkdir(parents=True, exist_ok=True)

        if len(paths) == 0:
            return

        bb = paths.bb()

        abs_scaled_bb = (
            abs(bb.x * scale),
            abs(bb.y * scale),
            abs((bb.x + bb.w) * scale),
            abs((bb.y + bb.h) * scale),
        )

        image_width = int(abs_scaled_bb[0] + abs_scaled_bb[2])
        image_height = int(abs_scaled_bb[1] + abs_scaled_bb[3])

        print(f"Creating image with size=({image_width}, {image_height})")
        assert image_width < 20000 and image_height < 20000, "keep resolution lower"

        img = Image.new("RGB", (image_width, image_height,), "white",)
        img_draw = ImageDraw.ImageDraw(img)

        it = PathIterator([paths])

        for conn in it.connections(scaled=False):
            start = conn[0]
            end = conn[1]

            # offset paths when passed bb starts in negative space
            if bb.x * scale < 0:
                start.x += abs_scaled_bb[0]
                end.x += abs_scaled_bb[0]

            if bb.y < 0:
                start.y += abs_scaled_bb[1]
                end.y += abs_scaled_bb[1]

            img_draw.line(
                xy=(start.x * scale, start.y * scale, end.x * scale, end.y * scale),
                fill="black",
                width=1,
            )

        fname = self.save_path.joinpath(filename + ".jpg")
        print(f"Saving to {fname}")
        img.save(fname, "JPEG")
