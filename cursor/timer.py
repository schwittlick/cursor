import pathlib
import time
import logging
import typing
from functools import wraps


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


def timing(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        timer = Timer()
        result = func(*args, **kwargs)
        code_obj = func.__code__
        func_name = func.__name__
        full_path = pathlib.Path(code_obj.co_filename)
        # will print e.g.: INFO: cursor/collection.py:584:fast_tsp(): 1231ms
        ff = f"{full_path.parent.name}/{full_path.name}:{code_obj.co_firstlineno}:{func_name}()"
        logging.info(f"{ff}: {round(timer.elapsed() * 1000)}ms")
        return result

    return wrapper
