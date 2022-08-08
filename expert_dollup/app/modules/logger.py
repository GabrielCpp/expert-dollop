from pythonjsonlogger import jsonlogger
from logging import Logger, basicConfig, INFO, DEBUG, getLogger, StreamHandler
from datetime import datetime, timezone
from injector import Binder, singleton
from expert_dollup.shared.starlette_injection import (
    LoggerFactory,
    PureBinding,
    is_development,
)

# TODO: Finish the loger
def bind_logger(binder: Binder) -> None:
    def add_timestamp(_, __, event_dict):
        event_dict["timestamp"] = str(datetime.now(timezone.utc).isoformat())
        return event_dict

    logger = getLogger()
    logHandler = StreamHandler()
    formatter = jsonlogger.JsonFormatter()
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
        to=lambda: PureBinding(lambda name: logger),
        scope=singleton,
    )
