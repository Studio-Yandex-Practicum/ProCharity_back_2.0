import structlog

from src.bot import create_bot
from src.core.logging.setup import setup_logging


if __name__ == "__main__":
    if not structlog.is_configured():
        setup_logging()
    create_bot().run_polling()
