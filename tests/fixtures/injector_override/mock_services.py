import pytest
from datetime import datetime, timezone
from logging import Logger
from injector import singleton
from expert_dollup.shared.starlette_injection import (
    Clock,
    StaticClock,
    LoggerFactory,
    LoggerObserver,
    PureBinding,
)


@pytest.fixture
def static_clock(container) -> Clock:
    clock = StaticClock(datetime(2000, 4, 3, 1, 1, 1, 0, timezone.utc))
    container.binder.bind(Clock, clock, scope=singleton)
    return clock


@pytest.fixture
def logger_observer(container) -> LoggerObserver:
    logger_observer = LoggerObserver()
    container.binder.bind(Logger, lambda: logger_observer, scope=singleton)
    container.binder.bind(
        LoggerFactory,
        lambda: PureBinding(lambda name: logger_observer),
        scope=singleton,
    )
    return logger_observer
