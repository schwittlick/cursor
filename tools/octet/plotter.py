import pathlib
import random
import typing
from random import randint
import time
import wasabi

from cursor import misc
from cursor.bb import BoundingBox
from cursor.collection import Collection
from cursor.device import MinmaxMapping, MaxSpeed
from cursor.filter import EntropyMinFilter, EntropyMaxFilter
from cursor.path import Path
from cursor.renderer import HPGLRenderer
from tools.octet.client import Client
from tools.octet.data import all_paths
from tools.octet.mouse import MouseThread
from tools.octet.plotterthread import PlotterThread

logger = wasabi.Printer(pretty=True, no_print=False)


class Plotter:
    def __init__(self, ip: str, port: int, serial_port: typing.Union[str, None], baud: int, timeout: float,
                 pen_count: int):
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
        self.max_pens = pen_count
        self.line_distance = 10

        self.__delay = 0.0

        self.__value1 = 0.0
        self.__value2 = 1000

        self.thread = PlotterThread(self.serial_port, self)
        self.thread.c = all_paths
        self.thread.speed = 40
        self.thread.start()

        self.mouse_thread = None

        self.last_col = None

    def __repr__(self):
        return f"{self.type} at {self.serial_port} online={self.is_connected}"

    def set_delay(self, delay: float):
        # coming straight from midi
        self.__delay = delay
        logger.info(f"plotter.delay = {self.__delay} -> {self.type}")

    def set_speed(self, speed: float):
        # coming straight from midi
        max_sped = MaxSpeed.fac[self.type]
        self.thread.speed = misc.map(speed, 0, 1000, 1, max_sped, True)
        logger.info(f"plotter.speed = {self.thread.speed} -> {self.type}")

    def set_value1(self, v1: float):
        logger.info(f"v1: {v1}")
        if self.thread.v1_label:
            self.thread.v1_label.text = str(int(v1))
        self.__value1 = v1

    def set_value2(self, v2: float):
        logger.info(f"v1: {v2}")
        if self.thread.v2_label:
            self.thread.v2_label.text = str(int(v2))
        self.__value2 = v2

    def set_line_distance(self, d):
        self.line_distance = misc.map(d, 0, 1000, 10, 50, True)
        self.thread.line_distance_label.text = str(int(self.line_distance))
        logger.info(f"setting line distance to {self.line_distance}")

    def get_value1(self, min, max) -> int:
        return int(misc.map(self.__value1, 0, 1000, min, max, True))

    def get_value2(self, min, max) -> int:
        return int(self.get_value2f(min, max))

    def get_value2f(self, min, max) -> float:
        return misc.map(self.__value2, 0, 1000, min, max, True)

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

        offset_x = random.randint(int(bounds.x), int(bounds.x2 - bounds.w * 0.9))
        offset_y = random.randint(int(bounds.y), int(bounds.y2 - bounds.h * 0.9))

        d = self.scale(c, 0.1, (offset_x, offset_y))

        out = Collection()
        transformed_line = d[0]
        # min = self.get_value1(1, 100)
        # max = self.get_value2(1, 100)
        # times = random.randint(min, max)
        times = self.get_value1(1, 100)
        for i in range(times):
            out.add(transformed_line.copy().offset(i * int(self.line_distance)))
        out[len(out) - 1].end_pos()
        self.xy = out[len(out) - 1].end_pos().as_tuple()

        for pa in d:
            pa.pen_select = self.current_pen
            pa.velocity = self.thread.speed
        data, duration = self.render(d)
        result, feedback = self.send_data(data)
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def go_to_pos(self, xy):
        bounds = MinmaxMapping.maps[self.type]
        new_pos_x = misc.map(xy[0], 0, 1, bounds.x, bounds.x2, True)
        new_pos_y = misc.map(xy[1], 0, 1, bounds.y, bounds.y2, True)
        result, feedback = self.send_data(
            f"SP{self.current_pen};VS{self.thread.speed};PU;PA{new_pos_x},{new_pos_y};")
        # print(f"done pen updown {result} + {feedback}")

        return feedback

    def mouse(self, col, speed):
        if not self.mouse_thread:

            self.mouse_thread = MouseThread(lambda xy, s=self: s.go_to_pos(xy))
            self.mouse_thread.start()
        else:
            self.mouse_thread.kill()
            self.mouse_thread.join()
            self.mouse_thread = None
            result, feedback = self.send_data("PU;")
            logger.info(f"PU; {result} -> {feedback}")

    def c73(self, col: Collection, speed):
        v2 = self.get_value2f(1.5, 5.5)
        fcol = col
        if self.last_col:
            last_col, last_v2 = self.last_col
            logger.info(f"v2: {v2} lastv2:{last_v2}")
            if last_v2 != v2:
                logger.warn(f"v2 c73: {v2}")

                # highpass filter
                fmin = EntropyMinFilter(v2 - 0.5, v2 - 0.5)
                fcol = col.filtered(fmin)

                # lowpass filter
                fmax = EntropyMaxFilter(v2 + 0.5, v2 + 0.5)
                fcol = fcol.filtered(fmax)

        self.last_col = fcol, v2

        line = fcol.random()
        line.velocity = self.thread.speed

        bounds = MinmaxMapping.maps[self.type]

        startx = random.randint(int(bounds.x), int(bounds.x2))
        starty = random.randint(int(bounds.y), int(bounds.y2))
        endx = random.randint(int(bounds.x), int(bounds.x2))
        endy = random.randint(int(bounds.y), int(bounds.y2))

        line = line.morph((startx, starty), (endx, endy))

        out = Collection()
        times = self.get_value1(1, 100)
        for i in range(times):
            out.add(line.copy().offset(i * int(self.line_distance)))

        last_line = out[len(out) - 1]
        self.xy = last_line.end_pos().as_tuple()

        self.send_speed(self.thread.speed)

        for pa in out:
            pa.pen_select = self.current_pen
        data, duration = self.render(out)
        result, feedback = self.send_data(data)
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def c83(self, col, speed):
        out = Collection()

        bounds = MinmaxMapping.maps[self.type]
        start_x = random.randint(int(bounds.x), int(bounds.x2))
        start_y = random.randint(int(bounds.y), int(bounds.y2))
        w = self.get_value1(10, 100)
        h = w
        step_size = random.randint(15, 35)  # 20 is good
        v2 = self.get_value2(0, 400)

        for y in range(h):
            for x in range(w):
                pos = (start_x + x * step_size, start_y + y * step_size)
                pos = (pos[0] + random.randint(-v2, v2), pos[1] + random.randint(-v2, v2))
                pa = Path.from_tuple_list([pos, pos])

                pa.pen_select = self.current_pen
                pa.velocity = self.thread.speed

                self.xy = pos
                out.add(pa)

        self.send_speed(self.thread.speed)

        data, duration = self.render(out)
        result, feedback = self.send_data(data)
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def small_line_field(self, col, speed):

        out = Collection()
        linecount = self.get_value1(1, 100)
        for i in range(linecount):
            c = Collection()

            line = col.random()
            line.velocity = self.thread.speed
            line.pen_select = self.current_pen
            c.add(line)

            bounds = MinmaxMapping.maps[self.type]
            start_x = random.randint(int(bounds.x), int(bounds.x2))
            start_y = random.randint(int(bounds.y), int(bounds.y2))
            random_w = random.randint(1, int(bounds.w / 100))
            random_h = random.randint(1, int(bounds.h / 100))
            c = self.transform(c, BoundingBox(start_x, start_y, start_x + random_w, start_y + random_h))
            for pa in c:
                out.add(pa.copy())

        data, duration = self.render(out)
        result, feedback = self.send_data(data)
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def signature(self, col, speed):
        # draw signature
        pass

    def __generate_line(self, start_x, start_y, end_x, end_y, num_points, rangex, rangey):
        """
        Generate a list of (x, y) points representing a straight line
        from (start_x, start_y) to (end_x, end_y), with num_points
        points that have slightly randomized y coordinates.
        """
        import random
        from noise import pnoise1
        points = []
        for i in range(num_points):
            x_noise_strength = 0.01
            y_noise_strength = 0.01
            y_random_strength = 0.05

            points = []
            for i in range(num_points):
                t = i / (num_points - 1)
                x = start_x + (end_x - start_x) * t
                y = start_y + (end_y - start_y) * t
                x_offset = x_noise_strength * pnoise1(random.random() + t * 10)
                y_offset = y_random_strength * (random.random() - 0.5) + y_noise_strength * pnoise1(
                    random.random() + t * 20)
                x += x_offset * rangex
                y += y_offset * rangey
                points.append((x, y))
        return points

    def chatgpt_simulated_mouse_movement(self, col, speed):
        point_count = self.get_value2(1, 100)
        out = Collection()
        bounds = MinmaxMapping.maps[self.type]
        start_x = random.randint(int(bounds.x), int(bounds.x2))
        start_y = random.randint(int(bounds.y), int(bounds.y2))
        end_x = random.randint(int(bounds.x), int(bounds.x2))
        end_y = random.randint(int(bounds.y), int(bounds.y2))
        points = self.__generate_line(start_x, start_y, end_x, end_y, point_count, bounds.w, bounds.h)
        path = Path.from_tuple_list(points)
        path.pen_select = self.current_pen

        times = self.get_value1(1, 100)
        for i in range(times):
            out.add(path.copy().offset(i * int(self.line_distance)))

        out.add(path)

        self.send_speed(self.thread.speed)
        for pa in out:
            pa.pen_select = self.current_pen
        data, duration = self.render(out)
        result, feedback = self.send_data(data)
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def init(self, c, speed):
        result, feedback = self.send_data(f"IN;SP1;LT;VS{speed};PA0,0;")
        self.xy = (0, 0)
        self.current_pen = 1

        return feedback

    def next_pen(self, c, speed):
        self.current_pen += 1
        if self.current_pen > self.max_pens:
            self.current_pen = 1
        self.thread.pen_label.text = str(self.current_pen)
        result, feedback = self.send_data(f"SP{self.current_pen};")

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
        # min = self.get_value1(1, 100)
        # max = self.get_value2(1, 100)
        # times = random.randint(min, max)
        times = self.get_value1(1, 100)

        # times = 2  # randint(1, 100)
        result, feedback = self.send_data(f"PD;PU;PA{self.xy[0]},{self.xy[1]};" * times)
        time.sleep(0.2)
        print(f"done pen updown {result} + {feedback}")

        return feedback

    def reset(self, col: Collection, speed):
        result, feedback = self.send_data("SP0;PA0,0;")
        self.current_pen = 0
        self.thread.pen_label.text = str(self.current_pen)

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
            for poi in pa.generate:
                poi.x = (poi.x * scale) + offset[0]
                poi.y = (poi.y * scale) + offset[1]
        return c

    def transform(self, c, dims):
        cbb = c.bb()
        trans = misc.transformFn((cbb.x, cbb.y), (cbb.x2, cbb.y2), (dims.x, dims.y), (dims.x2, dims.y2))
        for pa in c:
            for poi in pa.generate:
                n_poi = trans(poi.as_tuple())
                poi.x = n_poi[0]
                poi.y = n_poi[1]
        return c

    def render(self, c: Collection):
        r = HPGLRenderer(pathlib.Path(""))
        r.add(c)
        seconds = r.estimated_duration(self.thread.speed)
        logger.info(f"this will take approx {seconds}s.")
        return r.generate_string(), seconds
