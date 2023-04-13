import logging
import sys

from loguru import logger

from src.settings import settings


class InterceptHandler(logging.Handler):
    """Класс для перехвата логов для loguru."""

    def emit(self, record):
        # Получаем соответствующий уровень логов loguru, если он есть.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Находим источник логируемого сообщения.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    logging.basicConfig(
        handlers=[InterceptHandler()], level=settings.LOG_LEVEL, force=True
    )

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    logger.remove()
    logger.add(sink=sys.stdout, level="INFO", enqueue=True)
    logger.add(
        sink=settings.LOG_LOCATION,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression=settings.LOG_COMPRESSION,
        level=settings.LOG_LEVEL,
        enqueue=True,
    )
