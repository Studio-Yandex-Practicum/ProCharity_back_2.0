from src.bot import create_bot
from src.core.logging import setup_logging

if __name__ == "__main__":
    setup_logging()
    create_bot().run_polling()
