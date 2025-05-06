from contextlib import contextmanager
from functools import wraps
from time import time

from ngi_calculations.cpt_correlations.utils.log import log

# A stack to keep track of the function names and log_child flag
_execution_stack = []


@contextmanager
def measure_time(label, log_child):
    start = int(round(time() * 1000))
    _execution_stack.append((label, log_child))
    try:
        yield
    finally:
        end_ = int(round(time() * 1000)) - start
        end_ = end_ if end_ > 0 else 0

        msg = f"** {end_:03} ms -> {label}"
        log.info(msg)
        _execution_stack.pop()


def measure(label: str, log_time: bool = True, log_child: bool = False):
    def decorator(func):
        @wraps(func)
        def _time_it(*args, **kwargs):
            if log_time:
                if log_child:
                    with measure_time(f"{label} - {func.__name__}", log_child=True):
                        return func(*args, **kwargs)
                else:
                    with measure_time(f"{label} - {func.__name__}", log_child=False):
                        return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return _time_it

    return decorator


def track_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _execution_stack and _execution_stack[-1][1]:
            label = f"{func.__module__}.{func.__qualname__}"
            with measure_time(label, log_child=False):
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return wrapper
