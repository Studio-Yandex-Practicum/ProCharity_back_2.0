from telegram.ext import Application

from src.settings import settings


def create_bot() -> Application:
    bot = Application.builder().token(settings.BOT_TOKEN).build()
    # TODO: Добавить хэндлеры
    # bot.add_handler(...)
    return bot


async def start_bot() -> Application:
    bot = create_bot()
    await bot.initialize()
    if settings.BOT_WEBHOOK_MODE:
        bot.updater = None
        await bot.bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.SECRET_KEY,
        )
    else:
        await bot.updater.start_polling()
    await bot.start()
    return bot
