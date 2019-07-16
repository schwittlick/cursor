class TimedPosition(object):
    def __init__(self, x, y, timestamp):
        self.x = x
        self.y = y
        self.timestamp = timestamp

    def __str__(self):
        x_str = "{0:.2f}".format(self.x)
        y_str = "{0:.2f}".format(self.y)
        return x_str + ' ' + y_str


class Path(object):
    vertices = []

    def add(self, x, y, timestamp):
        self.vertices.append(TimedPosition(x, y, timestamp))

    def clear(self):
        self.vertices.clear()

    def copy(self):
        newone = type(self)()
        newone.vertices = self.vertices.copy()
        return newone

    def start_pos(self):
        if len(self.vertices) == 0:
            raise IndexError
        return self.vertices[0]

    def end_pos(self):
        if len(self.vertices) == 0:
            raise IndexError

        return self.vertices[-1]

    def __str__(self):
        return_string = ''
        for vertex in self.vertices:
            return_string += str(vertex) + ' '
        return return_string

    def __len__(self):
        return len(self.vertices)


class PathCollection(object):
    def __init__(self, resolution):
        self.paths = []
        self.resolution = resolution

    def add(self, path, resolution):
        if resolution.width != self.resolution.width or resolution.height != self.resolution.height:
            raise Exception('New resolution is different to current. This should be handled somehow ..')
        self.paths.append(path)

    def __str__(self):
        return_string = ''
        for path in self.paths:
            return_string += str(path) + '\n'
        return return_string