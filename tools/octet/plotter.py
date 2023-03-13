import pathlib
from random import randint
import math

import wasabi

from cursor.timer import Timer
from cursor.collection import Collection
from cursor.device import PlotterType, PaperSize, XYFactors, Paper, MinmaxMapping
from cursor.renderer import HPGLRenderer
from tools.octet.client import Client
from tools.octet.data import all_paths
from tools.octet.gui import GuiThread

logger = wasabi.Printer(pretty=True, no_print=False)


class Plotter:
    def     __init__(self, ip: str, port: int, serial_port: str, baud: int, timeout: float):
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

    @staticmethod
    def draw_random_line(plotter: "Plotter", col: Collection, speed):
        try:
            c = Collection()
            line = col.random()
            line.velocity = speed
            c.add(line)
            d = Plotter.rendering(c, plotter.type)
            plotter.xy = line.end_pos().as_tuple()

            result, feedback = plotter.send_data(d)
            logger.info(f"{result} : {feedback}")
            return feedback
        except Exception as e:
            logger.fail(e.__traceback__.tb_lineno)
            logger.fail(f"FAILED {e}")

    @staticmethod
    def init(plo, c, speed):
        result, feedback = plo.send_data(f"IN;SP1;LT;VS{speed};PA0,0;")
        plo.xy = (0, 0)

        print(f"done init  {result} + {feedback}")

        return feedback

    @staticmethod
    def go_up_down(plotter: "Plotter", col: Collection, speed):
        d = MinmaxMapping.maps[plotter.type]
        result, feedback = plotter.send_data(f"PA{d.x},{0};PA{d.w},{0};PD;PU;")
        plotter.xy = (d.w, 0)

        print(f"done with updown {result} + {feedback}")

        return feedback

    @staticmethod
    def random_pos(plotter: "Plotter", col: Collection, speed):
        d = MinmaxMapping.maps[plotter.type]
        x = randint(d.x, d.x2)
        y = randint(d.y, d.y2)

        result, feedback = plotter.send_data(f"PD;PA{randint(d.x, d.x2)},{randint(d.y, d.y2)};PU;" * 10)

        print(f"random_pos done {result} + {feedback}")

        return feedback

    @staticmethod
    def pen_down_up(plotter: "Plotter", col: Collection, speed):
        times = randint(1, 100)
        result, feedback = plotter.send_data(f"PD;PU;PA{plotter.xy[0]},{plotter.xy[1]};" * times)

        print(f"done pen updown {result} + {feedback}")

        return feedback

    @staticmethod
    def set_speed(plotter: "Plotter", col: Collection, speed):
        global global_speed
        logger.info(f"sending speed {global_speed}")
        result, feedback = plotter.send_data(f"VS{global_speed};")

        print(f"done set speed {result} + {feedback}")

        return feedback

    @staticmethod
    def rendering(c: Collection, tt: PlotterType) -> str:
        dims = MinmaxMapping.maps[tt]
        trans = Plotter.transformFn((c.bb().x, c.bb().y), (c.bb().x2, c.bb().y2), (dims.x, dims.y), (dims.x2, dims.y2))
        for pa in c:
            for poi in pa.vertices:
                n_poi = trans(poi.as_tuple())
                poi.x = n_poi[0]
                poi.y = n_poi[1]

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
