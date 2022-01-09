from functools import wraps
from time import perf_counter


def log_execution_time_async(fn):
    @wraps(fn)
    async def time_it(*args, **kwargs):
        before = perf_counter()
        result = await fn(*args, **kwargs)
        after = perf_counter()
        print(f"{fn.__name__} executed in {after - before} seconds")
        return result

    return time_it


def log_execution_time(fn):
    @wraps(fn)
    def time_it(*args, **kwargs):
        before = perf_counter()
        result = fn(*args, **kwargs)
        after = perf_counter()
        print(f"{fn.__name__} executed in {after - before} seconds")
        return result

    return time_it


class StopWatch:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.before = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        after = perf_counter()
        print(f"{self.name} executed in {after - self.before} seconds")
