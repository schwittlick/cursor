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

from cursor.collection import Collection
from cursor.device import PlotterType, MinmaxMapping
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

    def set_cb(self, cb):
        self.task_completed_cb = cb

    def add(self, func, delay: float = 0.0):
        logger.info(f"Added {func.__name__} to {self.plotter.type} with delay {delay}")
        self.buffer.put(func)
        self.delays.put(delay)

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
                    s = self.buffer.qsize()

                    time.sleep(delay)

                    if not self.plotter.serial_port:
                        # default time of task
                        self.thread_count.text = str(s)
                        if self.task_completed_cb:
                            self.task_completed_cb(s)
                        continue

                    try:

                        # run
                        func(self.plotter, self.c, self.speed)

                        if self.task_completed_cb:
                            self.task_completed_cb(s)

                    except socket.timeout as e:
                        logger.fail(f"{self.plotter.type} at {self.plotter} timed out")
                    except Exception as e:
                        logger.fail(f"Scheduled call failed: {e}")
                        logger.fail(f"{traceback.format_exc()}")

                else:
                    time.sleep(0.1)
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

        self.thread = GuiThread(self.serial_port, self)
        self.thread.c = all_paths
        self.thread.speed = 40
        self.thread.start()

    def __repr__(self):
        return f"{self.serial_port}"

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
        d = Plotter.rendering(c, self.type)
        self.xy = line.end_pos().as_tuple()

        result, feedback = self.send_data(d)
        logger.info(f"{self.type} : {result} : {feedback}")
        return feedback

    @staticmethod
    def c73(plotter: "Plotter", col: Collection, speed):
        c = Collection()

        line = col.random()
        line.velocity = plotter.thread.speed

        for i in range(10):
            l = line.copy()
            l.translate(1, 0)
            c.add(l)

        bounds = MinmaxMapping.maps[plotter.type]
        offset_x = random.randint(0, int(bounds.w * 0.8))
        offset_y = random.randint(0, int(bounds.h * 0.8))
        d = Plotter.rendering(c, plotter.type, 0.1, (offset_x, offset_y))
        plotter.xy = line.end_pos().as_tuple()

        result, feedback = plotter.send_data(d)
        logger.info(f"{plotter.type} : {result} : {feedback}")
        return feedback

    @staticmethod
    def init(plo, c, speed):
        result, feedback = plo.send_data(f"IN;SP1;LT;VS{speed};PA0,0;")
        plo.xy = (0, 0)

        print(f"done init  {result} + {feedback}")

        return feedback

    @staticmethod
    def take_pen(plo, c, speed):
        result, feedback = plo.send_data(f"SP1;")

        print(f"done init  {result} + {feedback}")

        return feedback

    @staticmethod
    def go_up_down(plotter: "Plotter", col: Collection, speed):
        d = MinmaxMapping.maps[plotter.type]
        result, feedback = plotter.send_data(f"PU;PA{d.x},{0};PA{d.w},{0};PD;PU;")
        plotter.xy = (d.w, 0)

        print(f"done with updown {result} + {feedback}")

        return feedback

    @staticmethod
    def random_pos(plotter: "Plotter", col: Collection, speed):
        d = MinmaxMapping.maps[plotter.type]
        x = randint(d.x, d.x2)
        y = randint(d.y, d.y2)
        plotter.xy = (x, y)

        result, feedback = plotter.send_data(f"PD;PA{randint(d.x, d.x2)},{randint(d.y, d.y2)};PU;" * 1)

        print(f"random_pos done {result} + {feedback}")

        return feedback

    @staticmethod
    def pen_down_up(plotter: "Plotter", col: Collection, speed):
        times = 2# randint(1, 100)
        result, feedback = plotter.send_data(f"PD;PU;PA{plotter.xy[0]},{plotter.xy[1]};" * times)

        print(f"done pen updown {result} + {feedback}")

        return feedback

    @staticmethod
    def set_speed(plotter: "Plotter", col: Collection, speed):
        logger.info(f"sending speed {plotter.thread.speed}")
        result, feedback = plotter.send_data(f"VS{plotter.thread.speed};")

        print(f"done set speed {result} + {feedback}")

        return feedback

    @staticmethod
    def rendering(c: Collection, tt: PlotterType, scale=1.0, offset=(0, 0)) -> str:
        dims = MinmaxMapping.maps[tt]
        trans = Plotter.transformFn((c.bb().x, c.bb().y), (c.bb().x2, c.bb().y2), (dims.x, dims.y), (dims.x2, dims.y2))
        for pa in c:
            for poi in pa.vertices:
                n_poi = trans(poi.as_tuple())
                poi.x = (n_poi[0] * scale) + offset[0]
                poi.y = (n_poi[1] * scale) + offset[1]

        r = HPGLRenderer(pathlib.Path(""))
        r.render(c)
        return r.generate_string()

    """
    ty lars wander 
    https://larswander.com/writing/centering-and-scaling/
    """

    @staticmethod
    def transformFn(stl, sbr, dtl, dbr):
        stlx, stly = stl;
        sbrx, sbry = sbr;
        dtlx, dtly = dtl;
        dbrx, dbry = dbr;

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
