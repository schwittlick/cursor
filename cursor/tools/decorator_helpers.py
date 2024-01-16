import pathlib
import typing
from functools import wraps

from cursor.timer import Timer


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
        timer.print_elapsed(ff)
        return result

    return wrapper


@timing
def fuckme(test):
    print(test)


if __name__ == "__main__":
    fuckme("letsgo")
