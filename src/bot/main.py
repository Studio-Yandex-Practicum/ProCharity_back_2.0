from telegram import Update
from telegram.ext import Application, TypeHandler

from src.core.logging.utils import logging_updates


def init_bot(telegram_bot: Application) -> Application:
    """Инициализация телеграм бота."""

    from .handlers import categories, menu, notifications, registration, tasks

    registration.registration_handlers(telegram_bot)
    categories.registration_handlers(telegram_bot)
    notifications.registration_handlers(telegram_bot)
    tasks.registration_handlers(telegram_bot)
    menu.registration_handlers(telegram_bot)
    telegram_bot.add_handler(TypeHandler(Update, logging_updates))
    return telegram_bot
