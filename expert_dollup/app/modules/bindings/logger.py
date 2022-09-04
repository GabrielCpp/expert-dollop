from pythonjsonlogger.jsonlogger import JsonFormatter
from typing import Dict, Any
from logging import (
    Logger,
    INFO,
    DEBUG,
    getLogger,
    StreamHandler,
    LoggerAdapter,
    root,
    getLevelName,
    LogRecord,
)
from datetime import datetime, timezone
from injector import Binder, singleton
from expert_dollup.shared.starlette_injection import (
    LoggerFactory,
    PureBinding,
    is_development,
)


class LoggerContext(LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"].update(self.extra)
        return msg, kwargs


class CustomJsonFormatter(JsonFormatter):
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        log_record["file"] = f"{record.pathname}:{record.lineno}"
        JsonFormatter.add_fields(self, log_record, record, message_dict)


def bind_logger(binder: Binder) -> None:
    LOG_LEVEL = DEBUG if is_development() else INFO
    json_formatter = CustomJsonFormatter(
        timestamp=True, static_fields=dict(level=getLevelName(LOG_LEVEL))
    )
    logHandler = StreamHandler()
    logHandler.setFormatter(json_formatter)

    root.handlers = [logHandler]
    root.setLevel(LOG_LEVEL)

    for name in root.manager.loggerDict.keys():
        getLogger(name).handlers = []
        getLogger(name).propagate = True

    logger = getLogger("expert_dollup")
    logger.propagate = True
    logger.setLevel(LOG_LEVEL)

    binder.bind(
        Logger,
        to=lambda: logger,
        scope=singleton,
    )
    binder.bind(
        LoggerFactory,
        to=lambda: PureBinding(
            lambda name: LoggerContext(logger, {"class_name": name})
        ),
        scope=singleton,
    )
