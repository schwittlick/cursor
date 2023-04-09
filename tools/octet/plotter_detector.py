import threading

import serial

from cursor.device import MaxSpeed, PlotterHpglNames
from tools.octet.discovery import discover
from tools.octet.plotter import Plotter


def attempt_detect(model, ip: str, tcp_port: int, serial_port: str, baud: int, timeout: float, pen_count: int):
    p = Plotter(ip, tcp_port, serial_port, baud, timeout, pen_count)
    p.connect()
    p.open_serial()

    for k, v in PlotterHpglNames.names.items():
        if v == model:
            p.type = k
            p.thread.speed = MaxSpeed.fac[k]
            return p

    return None


class PlotterDetector:
    def __init__(self, _tcp_port, _timeout, _pen_count, _target):
        self.ip = _target
        self.tcp_port = _tcp_port

        self.baudrate = 9600
        self.stopbits = serial.STOPBITS_ONE
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.xonxoff = False
        self.timeout = _timeout

        self.pen_count = _pen_count

    def detect(self):
        discovered = discover(baudrate=self.baudrate, stopbits=self.stopbits, bytesize=self.bytesize,
                              parity=self.parity, xonxoff=self.xonxoff, timeout=self.timeout)

        results = []

        threads = []
        for plo in discovered:
            if not plo:
                continue
            serial_port = plo[0]
            model = plo[1]

            thread = threading.Thread(
                target=lambda: results.append(
                    attempt_detect(model, self.ip, self.tcp_port, serial_port, self.baudrate, self.timeout,
                                   self.pen_count))
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        results = sorted(
            results,
            key=lambda x: x.type.value
        )

        return results
