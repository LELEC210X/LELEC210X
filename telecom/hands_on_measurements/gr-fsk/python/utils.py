import atexit
import statistics as stats

from functools import wraps
from time import time
from typing import Any, Callable, List


def timeit(fun: Callable[..., Any]) -> Callable[..., Any]:
    """
    Wrapper around a function and registers timing statistics about it.

    When the program exits (e.g., with CTRL + C), this utility
    will print short message with mean execution duration.

    Usage:

        Say you have a function definition:

        >>> def my_function(a, b):
        ...     pass

        You can simply use this utility as follows:

        >>> from .utils import timeit
        >>>
        >>> @timeit
        ... def my_function(a, b):
        ...     pass

    Note that you can use this decorator as many times as you want.
    """
    f_name = getattr(fun, "__name__", "<unnamed function>")
    data: List[float] = []

    def print_stats() -> None:
        mean = stats.mean(data)
        std = stats.stdev(data)
        print(f"{f_name} statistics: mean execution time of {mean:.2}s. (std: {std:.2}s.)")

    @wraps(fun)
    def wrapper(*args, **kwargs):
        start = time()
        ret = fun(*args, **kwargs)
        end = time()
        data.append(end - start)
        return ret

    atexit.register(print_stats)

    return wrapper
