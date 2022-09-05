from typing import Dict, Any
from datetime import datetime, timezone
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
from pythonjsonlogger.jsonlogger import JsonFormatter
from expert_dollup.shared.starlette_injection import *


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


def bind_logger(builder: InjectorBuilder) -> None:
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

    builder.add_object(Logger, logger)
    builder.add_singleton(
        LoggerFactory,
        lambda: PureBinding(lambda name: LoggerContext(logger, {"class_name": name})),
    )
