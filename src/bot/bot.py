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
    await bot.updater.start_polling()
    await bot.start()
    return bot
