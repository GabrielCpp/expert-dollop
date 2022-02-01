from abc import ABC, abstractmethod
from datetime import datetime, timezone


class Clock(ABC):
    @abstractmethod
    def utcnow(self) -> datetime:
        pass


class DateTimeClock(Clock):
    def utcnow(self) -> datetime:
        return datetime.now(timezone.utc).replace(microsecond=0)


class StaticClock(Clock):
    def __init__(self, fixed_time: datetime):
        self.fixed_time = fixed_time

    def utcnow(self) -> datetime:
        return self.fixed_time
