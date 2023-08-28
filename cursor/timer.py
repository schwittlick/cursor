import time
import logging

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class Timer:
    def __init__(self):
        self._time = None
        self.start()

    def start(self):
        self._time = time.perf_counter()

    def elapsed(self):
        t1 = time.perf_counter()
        return t1 - self._time

    def print_elapsed(self, msg: str = "") -> None:
        logging.info(f"{msg}: {round(self.elapsed() * 1000)}ms")
