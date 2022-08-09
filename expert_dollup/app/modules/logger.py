from pythonjsonlogger import jsonlogger
from logging import (
    Logger,
    basicConfig,
    INFO,
    DEBUG,
    getLogger,
    StreamHandler,
    LoggerAdapter,
)
from datetime import datetime, timezone
from injector import Binder, singleton
from expert_dollup.shared.starlette_injection import (
    LoggerFactory,
    PureBinding,
    is_development,
)


def bind_logger(binder: Binder) -> None:
    logger = getLogger()
    logHandler = StreamHandler()
    formatter = jsonlogger.JsonFormatter(timestamp=True)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    basicConfig(level=DEBUG if is_development() else INFO)

    binder.bind(
        Logger,
        to=lambda: logger,
        scope=singleton,
    )
    binder.bind(
        LoggerFactory,
        to=lambda: PureBinding(lambda name: LoggerAdapter(logger, {"name": name})),
        scope=singleton,
    )
