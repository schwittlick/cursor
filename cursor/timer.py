import pathlib
import time
import logging
import typing
from functools import wraps
import datetime

import pytz


class Timer:
    def __init__(self) -> None:
        self._time: float = None
        self.start()

    def start(self) -> None:
        self._time = time.perf_counter()

    def elapsed(self) -> float:
        t1 = time.perf_counter()
        return t1 - self._time

    def print_elapsed(self, msg: str = "") -> None:
        logging.info(f"{msg}: {round(self.elapsed() * 1000)}ms")

    @staticmethod
    def timestamp(timestamp_format: str = "%y%m%d_%H%M%S") -> str:
        now = datetime.datetime.now()
        return Timer.format_timestamp(now, timestamp_format)

    @staticmethod
    def format_timestamp(timestamp: datetime.datetime, timestamp_format: str = "%y%m%d_%H%M%S") -> str:
        return timestamp.strftime(timestamp_format)


def timing(func: typing.Callable) -> typing.Callable:
    @wraps(func)
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
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


class DateHandler:
    @staticmethod
    def utc_timestamp() -> float:
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        utc_timestamp = datetime.datetime.timestamp(now)
        return utc_timestamp

    @staticmethod
    def datetime_from_timestamp(ts: float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(ts)

    @staticmethod
    def get_timestamp_from_utc(ts: float) -> str:
        dt = DateHandler.datetime_from_timestamp(ts)
        return dt.strftime("%d/%m/%y %H:%M:%S.%f")
