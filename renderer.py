import svgwrite
import os
from PIL import Image, ImageDraw


class PathIterator:
    def __init__(self, paths):
        self.paths = paths

    def points(self):
        for collection in self.paths:
            for path in collection.paths:
                for point in path.vertices:
                    yield point, collection.resolution

    def connections(self, scaled=False):
        prev = None

        for collection in self.paths:
            for path in collection.paths:
                is_first_vertex = True
                for point in path.vertices:
                    if is_first_vertex:
                        prev = point.copy()
                        is_first_vertex = False

                        continue

                    start = prev
                    end = point.copy()
                    prev = point.copy()

                    if scaled:
                        start.scale(collection.resolution.width, collection.resolution.height)
                        end.scale(collection.resolution.width, collection.resolution.height)

                    yield start, end


class CursorSVGRenderer:
    def __init__(self):
        self.save_path = 'data/svgs/'

    def render(self, paths, resolution, filename):
        dwg = svgwrite.Drawing(self.save_path + filename + '.svg', profile='tiny', size=(resolution.width, resolution.height))

        it = PathIterator(paths)
        for conn in it.connections(scaled=False):
            start = conn[0]
            end = conn[1]

            dwg.add(dwg.line(start.pos(), end.pos(), stroke=svgwrite.rgb(0, 0, 0, '%')))

        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        dwg.save()


class CursorGCodeRenderer:
    def __init__(self):
        self.save_path = 'data/gcode/'
        self.z_down = 4.5
        self.z_up = 0.0
        self.feedrate_xy = 2000
        self.feedrate_z = 1000
        self.invert_y = True

    def render(self, paths, filename):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        with open(self.save_path + filename + '.nc', 'w') as file:
            file.write(F'G01 Z0.0 F{self.feedrate_z}\n')
            file.write(F'G01 X0.0 Y0.0 F{self.feedrate_xy}\n')
            for collection in paths:
                min = collection.min()
                max = collection.max()
                print(min, max)
                for path in collection.paths:
                    x = path.start_pos().x
                    y = path.start_pos().y
                    if self.invert_y:
                        y = -y
                    file.write(F'G01 X{x:.4f} Y{y:.4f} F{self.feedrate_xy}\n')
                    file.write(F'G01 Z{self.z_down} F{self.feedrate_z}\n')
                    for line in path.vertices:
                        x = line.x
                        y = line.y
                        if self.invert_y:
                            y = -y
                        file.write(F'G01 X{x:.4f} Y{y:.4f} F{self.feedrate_xy}\n')
                    file.write(F'G01 Z{self.z_up} F{self.feedrate_z}\n')


class JpegRenderer:
    def __init__(self):
        self.save_path = 'data/jpgs/'

    def render(self, paths, resolution, filename):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        img = Image.new('RGB', (resolution.width, resolution.height), 'white')
        img_draw = ImageDraw.ImageDraw(img)

        it = PathIterator(paths)

        for conn in it.connections(scaled=False):
            start = conn[0]
            end = conn[1]

            img_draw.line(xy=(start.x, start.y, end.x, end.y), fill='black', width=1)

        img.save(self.save_path + filename + '.jpg', 'JPEG')
