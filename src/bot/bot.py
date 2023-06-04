import logging

from telegram.ext import AIORateLimiter, Application, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext.filters import StatusUpdate

from src.bot.constants.callback_data import ASK_YOUR_QUESTION, CONFIRM_CATEGORIES, SEND_ERROR_OR_PROPOSAL
from src.bot.handlers import (
    ask_your_question,
    back_subcategory_callback,
    categories_callback,
    confirm_categories_callback,
    menu_callback,
    select_subcategory_callback,
    start_command,
    subcategories_callback,
    web_app_data,
)
from src.settings import settings
from src.core.logging.utils import logging_updates


def create_bot() -> Application:
    bot = Application.builder().token(settings.BOT_TOKEN).rate_limiter(AIORateLimiter()).build()
    bot.add_handler(CommandHandler("start", start_command))
    bot.add_handler(CommandHandler("menu", menu_callback))
    bot.add_handler(CommandHandler("categories", categories_callback))
    bot.add_handler(CallbackQueryHandler(categories_callback, pattern="change_category"))
    bot.add_handler(CallbackQueryHandler(subcategories_callback, pattern=r"category_(\d+)"))
    bot.add_handler(CallbackQueryHandler(ask_your_question, pattern=ASK_YOUR_QUESTION))
    bot.add_handler(CallbackQueryHandler(ask_your_question, pattern=SEND_ERROR_OR_PROPOSAL))
    bot.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))
    bot.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=r"select_category_(\d+)"))
    bot.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=r"back_to_(\d+)"))
    bot.add_handler(CallbackQueryHandler(confirm_categories_callback, pattern=CONFIRM_CATEGORIES))
    bot.add_handler(CallbackQueryHandler(logging_updates))

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
