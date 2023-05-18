import json
import logging

from telegram.ext import AIORateLimiter, Application, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext.filters import StatusUpdate

from src.bot.handlers import (categories_callback, menu_callback, start_command,
                              subcategories_callback, web_app_data, ask_your_question)
from src.settings import settings


def create_bot() -> Application:
    bot = Application.builder().token(settings.BOT_TOKEN).rate_limiter(AIORateLimiter()).build()
    bot.add_handler(CommandHandler("start", start_command))
    bot.add_handler(CommandHandler("menu", menu_callback))
    bot.add_handler(CommandHandler("categories", categories_callback))
    bot.add_handler(CallbackQueryHandler(categories_callback, pattern="change_category"))
    bot.add_handler(CallbackQueryHandler(subcategories_callback, pattern=r"category_\d+"))
    bot.add_handler(CallbackQueryHandler(ask_your_question, pattern="ask_your_question"))
    bot.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))
    return bot


async def start_bot() -> Application:
    """Запуск бота в `Background` режиме."""
    bot = create_bot()
    if settings.BOT_WEBHOOK_MODE:
        await bot.bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.SECRET_KEY,
        )
    else:
        await bot.initialize()
        await bot.updater.start_polling()
    await bot.start()
    logging.info("Bot started")
    return bot
