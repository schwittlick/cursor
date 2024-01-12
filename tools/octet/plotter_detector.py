import threading

import serial
import wasabi

from cursor.device import MaxSpeed, PlotterHpglNames
from cursor.hpgl.discovery import discover
from tools.octet.plotter import Plotter

logger = wasabi.Printer(pretty=True, no_print=False)


def attempt_detect(model, ip: str, tcp_port: int, serial_port: str, baud: int, timeout: float, pen_count: int):
    p = Plotter(ip, tcp_port, serial_port, baud, timeout, pen_count)
    p.connect()
    p.open_serial()

    p_names = PlotterHpglNames.names
    for plotter_configs in p_names.keys():
        if model in plotter_configs:
            p_type = plotter_configs[model][
                0]  # a little shortcut here. the 0th index is not necessarily the plotter config we think this is. Could have differnt paper size
            p.type = p_type
            p.thread.speed = MaxSpeed.fac[p_type]
            return p

    return None


class PlotterDetector:
    def __init__(self, target, tcp_port, timeout, pen_count=1, baud=9600, stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, xonxoff=False):
        self.ip = target
        self.tcp_port = tcp_port
        self.timeout = timeout

        self.pen_count = pen_count

        self.baudrate = baud
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.parity = parity
        self.xonxoff = xonxoff

    def detect(self):
        p_discovered = discover(baudrate=self.baudrate, stopbits=self.stopbits, bytesize=self.bytesize,
                                parity=self.parity, xonxoff=self.xonxoff, timeout=self.timeout)
        valid_plotters = []
        threads = []

        for p in p_discovered:
            if not p:
                continue
            serial_port = p[0]
            model_name_oi = p[1]

            thread = threading.Thread(
                target=lambda: valid_plotters.append(
                    attempt_detect(model_name_oi, self.ip, self.tcp_port, serial_port, self.baudrate, self.timeout,
                                   self.pen_count))
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        valid_plotters.sort(key=lambda x: x.type.value)
        return valid_plotters


if __name__ == '__main__':
    pd = PlotterDetector("localhost", 12345, 0.5)
    plotters = pd.detect()
    logger.info(plotters)
