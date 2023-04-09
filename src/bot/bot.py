from telegram.ext import Application, CommandHandler

from src.settings import settings

from .handlers import start_callback


async def create_bot() -> Application:
    bot = Application.builder().token(settings.BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start_callback))
    await bot.initialize()
    if settings.BOT_WEBHOOK_MODE:
        bot.updater = None
        await bot.bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.SECRET_KEY,
        )
    else:
        await bot.updater.start_polling()

    return bot


async def start_bot() -> Application:
    bot = await create_bot()
    await bot.start()
    return bot
