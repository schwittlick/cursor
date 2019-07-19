import svgwrite
import os
import loader


class CursorSVGRenderer:
    def __init__(self):
        self.SAVE_PATH = 'data/svgs/'

    def render(self, paths, size):
        dwg = svgwrite.Drawing(self.SAVE_PATH + 'test.svg', profile='tiny', size=size)

        prev_x = None
        prev_y = None
        for collection in paths:
            print(type(collection))
            for path in collection.paths:
                is_first_vertex = True
                print(path)
                for point in path.vertices:
                    if is_first_vertex:
                        prev_x = point.x
                        prev_y = point.y
                        is_first_vertex = False

                        continue

                    x1 = prev_x
                    y1 = prev_y

                    x2 = point.x
                    y2 = point.y

                    dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 0, 0, '%')))

                    prev_x = x2
                    prev_y = y2

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


if __name__ == "__main__":
    path = 'data/recordings/'
    loader = loader.Loader(path=path)

    rec = loader.all()

    vis = CursorSVGRenderer()
    vis.render(rec, (1920, 1080))

    gc = CursorGCodeRenderer()
    gc.render(rec)