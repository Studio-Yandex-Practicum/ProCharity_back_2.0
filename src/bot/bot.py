from telegram.ext import Application, CommandHandler

from src.settings import settings

from .handlers import start_callback


def create_bot() -> Application:
    bot = Application.builder().token(settings.BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start_callback))
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
    return bot
