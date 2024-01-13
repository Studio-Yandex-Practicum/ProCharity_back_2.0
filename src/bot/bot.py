import structlog
from telegram.ext import AIORateLimiter, Application

log = structlog.get_logger()


def create_bot(bot_token) -> Application:
    bot = Application.builder().token(bot_token).rate_limiter(AIORateLimiter()).build()
    return bot


async def start_bot(
    bot: Application, bot_webhook_mode: bool, telegram_webhook_url: str, telegram_secret_token: str
) -> Application:
    """Запуск бота в `Background` режиме."""
    await bot.initialize()
    if bot_webhook_mode is True:
        bot.updater = None
        await bot.bot.set_webhook(
            url=telegram_webhook_url,
            secret_token=telegram_secret_token,
        )
    else:
        await bot.updater.start_polling()  # type: ignore
    await bot.start()
    await log.ainfo("Bot started")
    return bot


async def startup_bot(
    bot: Application, bot_webhook_mode: bool, telegram_webhook_url: str, telegram_secret_token: str
) -> Application:
    bot_instance = await start_bot(bot, bot_webhook_mode, telegram_webhook_url, telegram_secret_token)
    result = await bot_instance.bot.setMyCommands(
        [
            [
                "start",
                "Запустить бота",
            ],
            [
                "menu",
                "Открыть меню",
            ],
        ]
    )
    await log.ainfo(result)
    return bot_instance


async def shutdown_bot(bot_instance, bot_webhook_mode: bool):
    if bot_webhook_mode is True:
        await bot_instance.updater.stop()
    await bot_instance.stop()
    await bot_instance.shutdown()
