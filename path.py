class TimedPosition(object):
    def __init__(self, x, y, timestamp):
        self.x = x
        self.y = y
        self.timestamp = timestamp


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
        return str(self.vertices)

    def __len__(self):
        return len(self.vertices)