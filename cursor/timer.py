import time
import wasabi

log = wasabi.Printer()


class Timer:
    def __init__(self):
        self.start()

    def start(self):
        self._time = time.perf_counter()

    def elapsed(self):
        t1 = time.perf_counter()
        return t1 - self._time

    def print_elapsed(self, msg):
        log.info(f"{msg}: {round(self.elapsed() * 1000)}ms")
