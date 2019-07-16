import svgwrite
import os
import loader


class CursorSVGRenderer(object):
    SAVE_PATH = 'data/svgs/'

    def __init__(self, ):
        pass

    def render(self, paths):

        dwg = svgwrite.Drawing(self.SAVE_PATH + 'test.svg', profile='tiny', size=(2500, 2500))

        prev_x = None
        prev_y = None
        for recording in paths:
            is_first_line = True
            print(type(recording))
            for line in recording.vertices:
                if is_first_line:
                    very_first = recording.vertices[0]
                    x1 = very_first.x
                    y1 = very_first.y
                    x2 = line.x
                    y2 = line.y
                    prev_x = x2
                    prev_y = y2
                else:
                    x1 = prev_x
                    y1 = prev_y
                    x2 = line.x
                    y2 = line.y
                    prev_x = x2
                    prev_y = y2
                print('drawing ' + str((x1, y1)) + ' to ' + str((x2, y2)))
                dwg.add(dwg.line((x1, y1), (x2, y2), stroke=svgwrite.rgb(0, 0, 0, '%')))

                is_first_line = False

        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)
        dwg.save()


class CursorGCodeRenderer(object):
    SAVE_PATH = 'data/gcode/'

    def __init__(self):
        self.z_down = 1.5
        self.z_up = 0.0

    def render(self, paths):
        if not os.path.exists(self.SAVE_PATH):
            os.makedirs(self.SAVE_PATH)

        with open(self.SAVE_PATH + 'test.gcode', 'w') as file:
            file.write('G00 X0.0 Y0.0 Z0.0\n')
            for recording in paths:
                file.write('G00 X' + str(recording.vertices[0].x) + ' Y' + str(recording.vertices[0].y) + '\n')
                file.write('G01 Z' + str(self.z_down) + '\n')
                for line in recording.vertices:
                    x = line.x
                    y = line.y
                    file.write('G01 X' + str(x) + ' Y' + str(y) + '\n')
                file.write('G00 Z' + str(self.z_up) + '\n')

if __name__ == "__main__":
    path = 'data/recordings/'
    loader = loader.Loader(path=path)

    rec = loader.get_all()

    vis = CursorSVGRenderer()
    vis.render(rec)

    gc = CursorGCodeRenderer()
    gc.render(rec)