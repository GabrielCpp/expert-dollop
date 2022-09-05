import pytest
from datetime import datetime, timezone
from logging import Logger
from expert_dollup.shared.starlette_injection import *


@pytest.fixture
def static_clock(container: TypedInjection) -> Clock:
    clock = StaticClock(datetime(2000, 4, 3, 1, 1, 1, 0, timezone.utc))
    container.bind_object(Clock, lambda: clock)
    return clock


@pytest.fixture
def logger_observer(container: TypedInjection) -> LoggerObserver:
    logger_observer = LoggerObserver()
    container.bind_object(Logger, lambda: logger_observer)
    container.bind_object(
        LoggerFactory, lambda: PureBinding(lambda name: logger_observer)
    )
    return logger_observer
