import pathlib
import random
import typing
from random import randint
import time
import wasabi

from cursor import misc
from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.device import PlotterType, MinmaxMapping, MaxSpeed
from cursor.path import Path
from cursor.renderer import HPGLRenderer
from tools.octet.client import Client
from tools.octet.data import all_paths
from tools.octet.mouse import MouseThread
from tools.octet.plotterthread import PlotterThread

logger = wasabi.Printer(pretty=True, no_print=False)


class Plotter:
    def __init__(self, ip: str, port: int, serial_port: typing.Union[str, None], baud: int, timeout: float):
        self.serial_port = serial_port
        self.baud = baud
        self.timeout = timeout
        self.ip = ip
        self.port = port
        self.client = Client(self.ip, self.port)
        self.client.set_timeout(timeout)
        self.is_connected = False
        self.msg_delimiter = '#'
        self.type = None

        self.xy = (0, 0)
        self.current_pen = 0
        self.max_pens = 3

        self.__delay = 0.0

        self.thread = PlotterThread(self.serial_port, self)
        self.thread.c = all_paths
        self.thread.speed = 40
        self.thread.start()

        self.mouse_thread = None

    def __repr__(self):
        return f"{self.type} at {self.serial_port} online={self.is_connected}"

    def set_delay(self, delay: float):
        # coming straight from midi (0-1000)
        self.__delay = delay / 300
        logger.info(f"plotter.delay = {self.__delay} -> {self.type}")

    def set_speed(self, speed: float):
        # coming straight from midi (0-1000)
        max_sped = MaxSpeed.fac[self.type]
        self.thread.speed = misc.map(speed, 0, 1000, 1, max_sped, True)
        logger.info(f"plotter.speed = {self.thread.speed} -> {self.type}")

    def get_delay(self):
        return self.__delay

    def __prefix(self):
        return f"{self.serial_port}{self.msg_delimiter}{self.baud}" \
               f"{self.msg_delimiter}{self.timeout}{self.msg_delimiter}"

    def connect(self):
        self.is_connected = self.client.connect()

    def disconnect(self):
        self.client.close()
        self.is_connected = False

    def send_data(self, data):
        self.client.send(f"{self.__prefix()}DATA{data}")
        return self.recv()

    def get_model(self):
        self.client.send(f"{self.__prefix()}OI;")
        return self.recv()

    def get_bounds(self):
        self.client.send(f"{self.__prefix()}OH;")
        return self.recv()

    def is_open_serial(self):
        self.client.send(f"{self.__prefix()}IS_OPEN")
        return self.recv()

    def open_serial(self):
        self.client.send(f"{self.__prefix()}OPEN")
        return self.recv()

    def close_serial(self):
        self.client.send(f"{self.__prefix()}CLOSE")
        return self.recv()

    def recv(self):
        return self.client.receive_feedback()

    def draw_random_line(self, col: Collection, speed):
        c = Collection()
        line = col.random()
        line.velocity = speed
        c.add(line)

        bounds = MinmaxMapping.maps[self.type]
        offset_x = random.randint(0, int(bounds.w * 0.8))
        offset_y = random.randint(0, int(bounds.h * 0.8))

        d = self.scale(c, 0.1, (offset_x, offset_y))
        self.xy = line.end_pos().as_tuple()

        for pa in d:
            pa.pen_select = self.current_pen
        result, feedback = self.send_data(self.render(d))
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def go_to_pos(self, xy):
        bounds = MinmaxMapping.maps[self.type]
        new_pos_x = misc.map(xy[0], 0, 3000, bounds.x, bounds.x2, True)
        new_pos_y = misc.map(xy[1], 0, 3000, bounds.y, bounds.y2, True)
        result, feedback = self.send_data(
            f"SP{self.current_pen};VS{self.thread.speed};PD;PA{new_pos_x},{new_pos_y};PU;")
        print(f"done pen updown {result} + {feedback}")

        return feedback

    def mouse(self, col, speed):
        if not self.mouse_thread:
            logger.info(f"starting mouse")

            self.mouse_thread = MouseThread(lambda xy, s=self: s.go_to_pos(xy))
            self.mouse_thread.start()
        else:
            logger.info(f"stopping mouse")
            self.mouse_thread.kill()
            self.mouse_thread.join()
            self.mouse_thread = None

    def c73(self, col: Collection, speed):
        c = Collection()

        line = col.random()
        line.velocity = self.thread.speed
        c.add(line)

        bounds = MinmaxMapping.maps[self.type]
        offset_x = random.randint(int(bounds.x), int(bounds.x2 - bounds.w * 0.4))
        offset_y = random.randint(int(bounds.y), int(bounds.y2 - bounds.h * 0.4))
        d = self.scale(c, 0.4, (offset_x, offset_y))

        out = Collection()
        transformed_line = d[0]
        for i in range(5):
            out.add(transformed_line.copy().offset(i * 10))

        last_line = out[len(out) - 1]
        self.xy = last_line.end_pos().as_tuple()

        self.send_speed(self.thread.speed)

        for pa in out:
            pa.pen_select = self.current_pen
        result, feedback = self.send_data(self.render(out))
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def c83(self, col, speed):
        out = Collection()

        bounds = MinmaxMapping.maps[self.type]
        start_x = random.randint(int(bounds.x), int(bounds.x2))
        start_y = random.randint(int(bounds.y), int(bounds.y2))
        random_w = random.randint(1, int(bounds.w / 100))
        random_h = random.randint(1, int(bounds.h / 100))
        for y in range(random_h):
            for x in range(random_w):
                pa = Path()
                pa.pen_select = self.current_pen
                pa.velocity = self.thread.speed
                pa.add(start_x + x, start_y + y)
                pa.add(start_x + x, start_y + y)
                self.xy = (start_x + x, start_y + y)
                out.add(pa)

        self.send_speed(self.thread.speed)

        result, feedback = self.send_data(self.render(out))
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def small_line_field(self, col, speed):
        c = Collection()

        line = col.random()
        line.velocity = self.thread.speed
        line.pen_select = self.current_pen
        c.add(line)
        out = Collection()
        for i in range(10):
            bounds = MinmaxMapping.maps[self.type]
            start_x = random.randint(int(bounds.x), int(bounds.x2))
            start_y = random.randint(int(bounds.y), int(bounds.y2))
            random_w = random.randint(1, int(bounds.w / 100))
            random_h = random.randint(1, int(bounds.h / 100))
            c = self.transform(c, BoundingBox(start_x, start_y, start_x + random_w, start_y + random_h))
            for pa in c:
                out.add(pa.copy())

        result, feedback = self.send_data(self.render(out))
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def init(self, c, speed):
        result, feedback = self.send_data(f"IN;SP1;LT;VS{speed};PA0,0;")
        self.xy = (0, 0)
        self.current_pen = 1

        print(f"done init  {result} + {feedback}")

        return feedback

    def next_pen(self, c, speed):
        self.current_pen += 1
        if self.current_pen > self.max_pens:
            self.current_pen = 1
        self.thread.pen_label.text = str(self.current_pen)
        result, feedback = self.send_data(f"SP{self.current_pen};")

        print(f"done init  {result} + {feedback}")

        return feedback

    def go_up_down(self, col: Collection, speed):
        d = MinmaxMapping.maps[self.type]
        result, feedback = self.send_data(f"PU;PA{d.x},{0};PA{d.w},{0};PD;PU;")
        self.xy = (d.w, 0)

        print(f"done with updown {result} + {feedback}")

        return feedback

    def random_pos(self, col: Collection, speed):
        d = MinmaxMapping.maps[self.type]
        x = randint(d.x, d.x2)
        y = randint(d.y, d.y2)
        self.xy = (x, y)

        # calculate time to draw it at current speed
        # speep for that long

        result, feedback = self.send_data(f"PD;PA{randint(d.x, d.x2)},{randint(d.y, d.y2)};PU;" * 1)

        print(f"random_pos done {result} + {feedback}")

        return feedback

    def pen_down_up(self, col: Collection, speed):
        times = 2  # randint(1, 100)
        result, feedback = self.send_data(f"PD;PU;PA{self.xy[0]},{self.xy[1]};" * times)
        time.sleep(0.2)
        print(f"done pen updown {result} + {feedback}")

        return feedback

    def reset(self, col: Collection, speed):
        result, feedback = self.send_data(f"SP0;PA0,0;")
        print(f"done pen updown {result} + {feedback}")
        self.current_pen = 0
        self.xy = (0, 0)

        return feedback

    def send_speed(self, speed):
        logger.info(f"sending speed {self.thread.speed}")
        result, feedback = self.send_data(f"VS{self.thread.speed};")

        print(f"done set speed {result} + {feedback}")

        return feedback

    def scale(self, c: Collection, scale=1.0, offset=(0, 0)) -> Collection:
        c = self.transform(c, MinmaxMapping.maps[self.type])

        for pa in c:
            for poi in pa.vertices:
                poi.x = (poi.x * scale) + offset[0]
                poi.y = (poi.y * scale) + offset[1]
        return c

    def transform(self, c, dims):
        cbb = c.bb()
        trans = Plotter.transformFn((cbb.x, cbb.y), (cbb.x2, cbb.y2), (dims.x, dims.y), (dims.x2, dims.y2))
        for pa in c:
            for poi in pa.vertices:
                n_poi = trans(poi.as_tuple())
                poi.x = n_poi[0]
                poi.y = n_poi[1]
        return c

    def render(self, c: Collection):
        r = HPGLRenderer(pathlib.Path(""))
        r.render(c)
        return r.generate_string()

    """
    ty lars wander 
    https://larswander.com/writing/centering-and-scaling/
    """

    @staticmethod
    def transformFn(stl, sbr, dtl, dbr):
        stlx, stly = stl
        sbrx, sbry = sbr
        dtlx, dtly = dtl
        dbrx, dbry = dbr

        sdx, sdy = sbrx - stlx, sbry - stly
        ddx, ddy = dbrx - dtlx, dbry - dtly

        ry, rx = ddx / sdx, ddy / sdy
        a = min(rx, ry)

        ox, oy = (ddx - sdx * a) * 0.5 + dtlx, (ddy - sdy * a) * 0.5 + dtly
        bx, by = -stlx * a + ox, -stly * a + oy

        def calc(inp):
            x, y = inp[0], inp[1]
            return x * a + bx, y * a + by

        return calc
