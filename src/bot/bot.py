import logging

from telegram.ext import AIORateLimiter, Application

from src.settings import settings


def create_bot(bot_token) -> Application:
    bot = Application.builder().token(bot_token).rate_limiter(AIORateLimiter()).build()
    return bot


async def start_bot(bot: Application) -> Application:
    """Запуск бота в `Background` режиме."""
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


async def startup_bot(bot: Application) -> Application:
    bot_instance = await start_bot(bot)
    return bot_instance


async def shutdown_bot(bot_instance):
    if not settings.BOT_WEBHOOK_MODE:
        await bot_instance.updater.stop()
    await bot_instance.stop()
    await bot_instance.shutdown()
