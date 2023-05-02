import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import structlog
from structlog.types import EventDict, Processor

from src.settings import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)


def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Uvicorn логирует сообщение повторно в дополнительной секции
    `color_message`, но нам это не нужно. Данная функция ("процессор")
    убирает данный ключ из event dict.
    """
    event_dict.pop("color_message", None)
    return event_dict


def setup_logging():
    """Настройки логирования."""
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.stdlib.ExtraAdder(),
        drop_color_message_key,
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.LOG_TO_JSON:
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer: structlog.types.Processor
    if settings.LOG_TO_JSON:
        log_renderer = structlog.processors.JSONRenderer()
    else:
        log_renderer = structlog.dev.ConsoleRenderer(
            exception_formatter=structlog.dev.rich_traceback
        )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    stream_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        os.path.join(settings.LOG_DIR, settings.LOG_FILE),
        maxBytes=settings.LOG_FILE_SIZE,
        backupCount=settings.LOG_FILES_TO_KEEP,
        encoding="UTF-8",
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    for _log in logging.root.manager.loggerDict.keys():
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False

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
