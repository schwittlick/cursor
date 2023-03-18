import pathlib
import random
import typing
from random import randint
import queue
import time
import threading
import wasabi
import traceback
import socket

from cursor import misc
from cursor.collection import Collection
from cursor.device import PlotterType, MinmaxMapping, MaxSpeed
from cursor.renderer import HPGLRenderer
from tools.octet.client import Client
from tools.octet.data import all_paths

logger = wasabi.Printer(pretty=True, no_print=False)


class GuiThread(threading.Thread):
    def __init__(self, thread_id, plotter):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.running = True
        self.plotter = plotter
        self.speed = None
        self.c = None
        self.stopped = False

        self.buffer = queue.Queue()
        self.delays = queue.Queue()

        # arcade flat ui buttons
        self.button = None
        self.thread_count = None

        self.task_completed_cb = None

        self.max_buffer_size = 50

    def set_cb(self, cb):
        self.task_completed_cb = cb

    def clear(self):
        while self.buffer.qsize() > 0:
            logger.info(f"Removing a task from {self.plotter}")
            self.buffer.get()
            self.delays.get()
            self.update_thread_count_ui()

    def add(self, func):
        current_delay = self.plotter.get_delay()
        logger.info(
            f"Added {func.__name__} to {self.plotter.type} at {self.plotter.serial_port} with delay {current_delay}")

        if self.buffer.qsize() >= self.max_buffer_size:
            logger.warn(f"Discarding ...")
            return
        self.buffer.put(func)
        self.delays.put(current_delay)

        self.update_thread_count_ui()

    def update_thread_count_ui(self):
        s = self.buffer.qsize()
        self.thread_count.text = "↔️ " + str(s)

    def run(self):
        logger.info(f"Thread for {self.plotter.type} at {self.plotter.serial_port} started")
        while True:
            if self.stopped:
                return

            if not self.running:
                time.sleep(0.1)
                continue
            else:
                if not self.buffer.empty():
                    func = self.buffer.get()
                    delay = self.delays.get()

                    self.update_thread_count_ui()
                    time.sleep(delay)

                    if not self.plotter.serial_port:
                        if self.task_completed_cb:
                            # TODO: callback
                            self.task_completed_cb()
                        continue

                    try:

                        # run
                        func(self.c, self.speed)

                        if self.task_completed_cb:
                            self.task_completed_cb()

                    except socket.timeout as e:
                        logger.fail(f"{self.plotter.type} at {self.plotter} timed out")
                    except Exception as e:
                        logger.fail(f"Scheduled call failed: {e}")
                        logger.fail(f"{traceback.format_exc()}")
                else:
                    time.sleep(0.01)
                    continue

        logger.info(f"Thread for {self.plotter.type} at {self.plotter.serial_port} finished")

    def stop(self):
        self.stopped = True

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True


class CheckerThread(threading.Thread):
    def __init__(self, plotters):
        threading.Thread.__init__(self)
        self.plotters = plotters
        self.running = True

    def run(self):
        while True:
            if not self.running:
                logger.info("Checker thread finished")
                return

            time.sleep(1)
            threads = {}
            for plo in self.plotters:
                threads[plo.serial_port] = plo

            dict_copy = threads.copy()
            for port, plo in dict_copy.items():
                if not plo.thread:
                    continue
                if not plo.thread.running:
                    plo.thread.pause()
                elif not plo.thread.is_alive():
                    plo.thread = None
                else:
                    # Resume the thread if it was paused
                    plo.thread.resume()

    def stop(self):
        self.running = False


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

        self.__delay = 0.0

        self.thread = GuiThread(self.serial_port, self)
        self.thread.c = all_paths
        self.thread.speed = 40
        self.thread.start()

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

        d = self.scale(c, self.type, 0.1, (offset_x, offset_y))
        self.xy = line.end_pos().as_tuple()

        result, feedback = self.send_data(self.render(d))
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def c73(self, col: Collection, speed):
        c = Collection()

        line = col.random()
        line.velocity = self.thread.speed
        c.add(line)

        bounds = MinmaxMapping.maps[self.type]
        offset_x = random.randint(0, int(bounds.w * 0.6))
        offset_y = random.randint(0, int(bounds.h * 0.6))
        d = self.scale(c, self.type, 0.4, (offset_x, offset_y))

        out = Collection()
        transformed_line = d[0]
        for i in range(5):
            out.add(transformed_line.copy().offset(i * 10))

        last_line = out[len(out) - 1]
        self.xy = last_line.end_pos().as_tuple()

        self.send_speed(self.thread.speed)

        result, feedback = self.send_data(self.render(out))
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    def init(self, c, speed):
        result, feedback = self.send_data(f"IN;SP1;LT;VS{speed};PA0,0;")
        self.xy = (0, 0)

        print(f"done init  {result} + {feedback}")

        return feedback

    def take_pen(self, c, speed):
        result, feedback = self.send_data(f"SP1;")

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

        return feedback

    def send_speed(self, speed):
        logger.info(f"sending speed {self.thread.speed}")
        result, feedback = self.send_data(f"VS{self.thread.speed};")

        print(f"done set speed {result} + {feedback}")

        return feedback

    def scale(self, c: Collection, tt: PlotterType, scale=1.0, offset=(0, 0)) -> Collection:
        dims = MinmaxMapping.maps[tt]
        cbb = c.bb()
        trans = Plotter.transformFn((cbb.x, cbb.y), (cbb.x2, cbb.y2), (dims.x, dims.y), (dims.x2, dims.y2))
        for pa in c:
            for poi in pa.vertices:
                n_poi = trans(poi.as_tuple())
                poi.x = (n_poi[0] * scale) + offset[0]
                poi.y = (n_poi[1] * scale) + offset[1]
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
