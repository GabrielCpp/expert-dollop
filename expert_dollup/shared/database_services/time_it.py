from functools import wraps
from time import perf_counter


def log_execution_time_async(fn):
    @wraps(fn)
    async def time_it(self, *args, **kwargs):
        before = perf_counter()
        result = await fn(self, *args, **kwargs)
        after = perf_counter()
        duration_in_seconds = after - before
        self.logger.debug(
            "Stopwatch scope measure",
            topic=fn.__name__,
            duration_in_seconds=duration_in_seconds,
        )
        return result

    return time_it


def log_execution_time(fn):
    @wraps(fn)
    def time_it(self, *args, **kwargs):
        before = perf_counter()
        result = fn(self, *args, **kwargs)
        after = perf_counter()
        duration_in_seconds = after - before
        self.logger.debug(
            "Stopwatch scope measure",
            topic=fn.__name__,
            duration_in_seconds=duration_in_seconds,
        )
        return result

    return time_it


class StopWatch:
    def __init__(self, logger, topic, message="Stopwatch scope measure"):
        self.logger = logger
        self.message = message
        self.topic = topic

    def __enter__(self):
        self.before = perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        after = perf_counter()
        duration_in_seconds = after - self.before
        self.logger.debug(
            self.message, topic=self.topic, duration_in_seconds=duration_in_seconds
        )
