from telegram import Update
from telegram.ext import Application, TypeHandler

from src.bot.handlers import categories, feedback_form, menu, registration, tasks
from src.core.logging.utils import logging_updates

from .bot import create_bot, start_bot

__all__ = (
    "start_bot",
    "create_bot",
)


def init_bot(telegram_bot: Application) -> Application:
    """Инициализация телеграм бота."""
    registration.registration_handlers(telegram_bot)
    categories.registration_handlers(telegram_bot)
    tasks.registration_handlers(telegram_bot)
    menu.registration_handlers(telegram_bot)
    feedback_form.registration_handlers(telegram_bot)
    telegram_bot.add_handler(TypeHandler(Update, logging_updates))
    return telegram_bot
