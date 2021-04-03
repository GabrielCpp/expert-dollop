import pytest
from datetime import datetime, timezone
from injector import singleton
from expert_dollup.shared.starlette_injection import Clock, StaticClock


@pytest.fixture
def static_clock(container):
    clock = StaticClock(datetime(2000, 4, 3, 1, 1, 1, 7, timezone.utc))
    container.binder.bind(Clock, clock, scope=singleton)
    return clock
