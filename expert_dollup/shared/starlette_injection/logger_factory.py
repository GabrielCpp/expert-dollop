from logging import Logger
from dataclasses import dataclass
from .late_binding import LateBinder


LoggerFactory = LateBinder[Logger, str]


@dataclass
class LogEntry:
    level: str
    msg: str
    args: list
    kwargs: dict


class LoggerObserver:
    def __init__(self):
        self.logs = []

    def debug(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("debug", msg, args, kwargs))

    def info(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("info", msg, args, kwargs))

    def warning(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("warning", msg, args, kwargs))

    def warn(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("warning", msg, args, kwargs))

    def error(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("error", msg, args, kwargs))

    def exception(self, msg, *args, exc_info=True, **kwargs):
        self.logs.append(LogEntry("error", msg, args, {"exc_info": exc_info, **kwargs}))

    def critical(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("critical", msg, args, kwargs))

    def fatal(self, msg, *args, **kwargs):
        self.logs.append(LogEntry("critical", msg, args, kwargs))

    def log(self, level, msg, *args, **kwargs):
        self.logs.append(LogEntry(level, msg, args, kwargs))