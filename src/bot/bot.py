import logging

from telegram import Update
from telegram.ext import AIORateLimiter, Application, TypeHandler

from src.bot.handlers import categories, feedback_form, menu, registration, tasks
from src.core.logging.utils import logging_updates
from src.settings import settings


def create_bot() -> Application:
    bot = Application.builder().token(settings.BOT_TOKEN).rate_limiter(AIORateLimiter()).build()

    registration.registration_handlers(bot)
    categories.registration_handlers(bot)
    tasks.registration_handlers(bot)
    menu.registration_handlers(bot)
    feedback_form.registration_handlers(bot)
    bot.add_handler(TypeHandler(Update, logging_updates))
    return bot


async def start_bot() -> Application:
    """Запуск бота в `Background` режиме."""
    bot = create_bot()
    await bot.initialize()
    if settings.BOT_WEBHOOK_MODE:
        bot.updater = None
        await bot.bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.SECRET_KEY,
        )
    else:
        await bot.updater.start_polling()  # type: ignore
    await bot.start()
    logging.info("Bot started")
    return bot


async def startup_bot():
    bot_instance = await start_bot()
    return bot_instance


async def shutdown_bot(bot_instance):
    if not settings.BOT_WEBHOOK_MODE:
        await bot_instance.updater.stop()
    await bot_instance.stop()
    await bot_instance.shutdown()
