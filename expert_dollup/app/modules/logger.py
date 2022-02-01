import structlog
from structlog.contextvars import merge_contextvars
from logging import Logger, basicConfig, INFO, DEBUG
from datetime import datetime, timezone
from injector import Binder, singleton
from expert_dollup.shared.starlette_injection import (
    LoggerFactory,
    PureBinding,
    is_development,
)


def bind_logger(binder: Binder) -> None:
    def add_timestamp(_, __, event_dict):
        event_dict["timestamp"] = str(datetime.now(timezone.utc).isoformat())
        return event_dict

    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            add_timestamp,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(),
            structlog.processors.JSONRenderer(indent=1, sort_keys=True),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    basicConfig(level=DEBUG if is_development() else INFO)

    binder.bind(
        Logger,
        to=lambda: structlog.get_logger(),
        scope=singleton,
    )
    binder.bind(
        LoggerFactory,
        to=lambda: PureBinding(lambda name: structlog.get_logger(name)),
        scope=singleton,
    )
