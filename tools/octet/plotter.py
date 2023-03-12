import pathlib
from random import randint

import wasabi

from cursor.collection import Collection
from cursor.device import PlotterType, PaperSize, XYFactors, Paper, MinmaxMapping
from cursor.renderer import HPGLRenderer
from tools.octet.client import Client

logger = wasabi.Printer(pretty=True, no_print=False)


class Plotter:
    def __init__(self, ip: str, port: int, serial_port: str, baud: int, timeout: float):
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
        self.thread = None
        self.button = None
        self.xy = (0, 0)

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
            logger.info(c)
            logger.info(plotter)
            d = Plotter.rendering(c, plotter.type)
            logger.info(d)
            plotter.xy = line.end_pos().as_tuple()

            result, feedback = plotter.send_data(d)
            logger.info(f"{result} : {feedback}")
            return feedback
        except Exception as e:
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
        c.fit(
            Paper.sizes[PaperSize.LANDSCAPE_A3],
            xy_factor=XYFactors.fac[tt],
            padding_mm=20,
            output_bounds=MinmaxMapping.maps[tt],
            keep_aspect=True
        )

        r = HPGLRenderer(pathlib.Path(""))
        r.render(c)
        return r.generate_string()
