import logging
import logging.config
import os
import sys

import structlog
from structlog.types import EventDict, Processor

from src.settings import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)


def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Uvicorn логирует сообщение повторно в дополнительной секции
    `color_message`, но нам это не нужно. Данная функция ("процессор")
    убирает данный ключ из event dict.
    """
    event_dict.pop("color_message", None)
    return event_dict


TIMESTAMPER = structlog.processors.TimeStamper(fmt="iso")

PRE_CHAIN: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.stdlib.ExtraAdder(),
    _drop_color_message_key,
    TIMESTAMPER,
    structlog.processors.StackInfoRenderer(),
]


LOGGING_DICTCONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(
                    colors=False,
                    exception_formatter=structlog.dev.plain_traceback,
                ),
            ],
            "foreign_pre_chain": PRE_CHAIN,
        },
        "colored": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            "foreign_pre_chain": PRE_CHAIN,
        },
    },
    "handlers": {
        "default": {
            "level": settings.LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "colored",
        },
        "file": {
            "level": settings.LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR, settings.LOG_FILE),
            "mode": "a",
            "maxBytes": settings.LOG_FILE_SIZE,
            "backupCount": settings.LOG_FILES_TO_KEEP,
            "encoding": "UTF-8",
            "formatter": "plain",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": True,
        },
    },
}


def _setup_structlog():
    """Настройки structlog."""

    logging.config.dictConfig(LOGGING_DICTCONFIG)

    structlog.configure(
        processors=PRE_CHAIN
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _setup_uvicorn_logging():
    """Настройки логирования uvicorn."""
    for _log in logging.root.manager.loggerDict.keys():
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False


def setup_logging():
    """Основные настройки логирования."""
    _setup_structlog()
    _setup_uvicorn_logging()

    root_logger = logging.getLogger()

    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Логирует любое непойманное исключение вместо его вывода на печать
        Python'ом (кроме KeyboardInterrupt, чтобы позволить Ctrl+C
        для остановки).
        См. https://stackoverflow.com/a/16993115/3641865
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error(
            "Непойманное исключение",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    sys.excepthook = handle_exception
