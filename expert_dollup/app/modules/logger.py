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
from fastapi.logger import logger as fastapi_logger


def bind_logger(binder: Binder) -> None:
    logHandler = StreamHandler()
    formatter = jsonlogger.JsonFormatter(timestamp=True)
    logHandler.setFormatter(formatter)

    fastapi_logger.addHandler(logHandler)
    logger = getLogger()
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
