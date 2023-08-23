import logging

from telegram.ext import AIORateLimiter, Application


def create_bot(bot_token) -> Application:
    bot = Application.builder().token(bot_token).rate_limiter(AIORateLimiter()).build()
    return bot


async def start_bot(
        bot: Application,
        BOT_WEBHOOK_MODE: bool,
        telegram_webhook_url: str,
        SECRET_KEY: str
) -> Application:
    """Запуск бота в `Background` режиме."""
    await bot.initialize()
    if BOT_WEBHOOK_MODE is True:
        bot.updater = None
        await bot.bot.set_webhook(
            url=telegram_webhook_url,
            secret_token=SECRET_KEY,
        )
    else:
        await bot.updater.start_polling()  # type: ignore
    await bot.start()
    logging.info("Bot started")
    return bot


async def startup_bot(
        bot: Application,
        BOT_WEBHOOK_MODE: bool,
        telegram_webhook_url: str,
        SECRET_KEY: str
) -> Application:
    bot_instance = await start_bot(bot, BOT_WEBHOOK_MODE, telegram_webhook_url, SECRET_KEY)
    return bot_instance


async def shutdown_bot(bot_instance, BOT_WEBHOOK_MODE: bool):
    if BOT_WEBHOOK_MODE is True:
        await bot_instance.updater.stop()
    await bot_instance.stop()
    await bot_instance.shutdown()
