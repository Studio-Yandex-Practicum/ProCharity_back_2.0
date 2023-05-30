import structlog

from src.bot import create_bot
from src.bot.bot import start_bot
from src.core.logging.setup import setup_logging
from src.settings import settings


async def startup_bot():
    bot_instance = await start_bot()
    return bot_instance


async def shutdown_bot(bot_instance):
    if not settings.BOT_WEBHOOK_MODE:
        await bot_instance.updater.stop()
    await bot_instance.stop()
    await bot_instance.shutdown()


if __name__ == "__main__":
    if not structlog.is_configured():
        setup_logging()
    create_bot().run_polling()
