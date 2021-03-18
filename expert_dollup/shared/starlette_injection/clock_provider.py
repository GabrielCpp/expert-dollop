from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    @abstractmethod
    def utcnow(self):
        pass


class DateTimeClock(Clock):
    def utcnow(self):
        return datetime.now(timezone.utc)


class StaticClock(Clock):
    def __init__(self, fixed_time: datetime):
        self.fixed_time = fixed_time

    def utcnow(self):
        return self.fixed_time