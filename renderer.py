from path import TimedPosition

import svgwrite
import os
import loader
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
        prev = TimedPosition()

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

                    yield start, end, collection.resolution


class CursorSVGRenderer:
    def __init__(self):
        self.SAVE_PATH = 'data/svgs/'

    def render(self, paths, size):
        dwg = svgwrite.Drawing(self.SAVE_PATH + 'test.svg', profile='tiny', size=size)

        it = PathIterator(paths)
        for conn in it.connections(scaled=True):
            start = conn[0]
            end = conn[1]

            dwg.add(dwg.line(start.pos(), end.pos(), stroke=svgwrite.rgb(0, 0, 0, '%')))

        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)
        dwg.save()


class CursorGCodeRenderer:
    def __init__(self):
        self.SAVE_PATH = 'data/gcode/'
        self.z_down = 1.5
        self.z_up = 0.0
        self.feedrate_up = 1000
        self.feedrate_down = 400
        self.invert_y = True

    def render(self, paths):
        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)

        with open(self.SAVE_PATH + 'test.gcode', 'w') as file:
            file.write('G00 X0.0 Y0.0 Z0.0\n')
            for collection in paths:
                min = collection.min()
                max = collection.max()
                print(min, max)
                for path in collection.paths:
                    x = path.start_pos().x * collection.resolution.width
                    y = path.start_pos().y * collection.resolution.height
                    if self.invert_y:
                        y = -y
                    file.write('G00 X' + str(x) + ' Y' + str(y) + '\n')
                    file.write('G01 Z' + str(self.z_down) + '\n')
                    for line in path.vertices:
                        x = line.x * collection.resolution.width
                        y = line.y * collection.resolution.height
                        if self.invert_y:
                            y = -y
                        file.write('G01 X' + str(x) + ' Y' + str(y) + '\n')
                    file.write('G00 Z' + str(self.z_up) + '\n')


class JpegRenderer:
    def __init__(self):
        pass

    def render(self, paths):
        img = Image.new('RGB', (3000, 3000), 'white')
        img_draw = ImageDraw.ImageDraw(img)

        it = PathIterator(paths)

        for conn in it.connections(scaled=True):
            start = conn[0]
            end = conn[1]

            img_draw.line(xy=(start.x, start.y, end.x, end.y), fill='black', width=3)

        img.save('custouttt.jpg', 'JPEG')



if __name__ == "__main__":
    path = 'data/recordings/'
    loader = loader.Loader(path=path)

    rec = loader.all()

    vis = CursorSVGRenderer()
    vis.render(rec, (1920, 1080))

    gc = CursorGCodeRenderer()
    gc.render(rec)

    jr = JpegRenderer()
    jr.render(rec)