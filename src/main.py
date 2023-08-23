from fastapi import FastAPI

from src.bot.bot import shutdown_bot, startup_bot
from src.core.utils import set_ngrok
from src.depends import Container

from src.api import init_app
from src.bot import init_bot


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
    fastapi_app = init_app(container.fastapi_app())
    bot = init_bot(container.telegram_bot())

    @fastapi_app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        if container.settings.provided.USE_NGROK is True:
            set_ngrok()
        if run_bot:
            fastapi_app.state.bot_instance = await startup_bot(
                bot=bot,
                BOT_WEBHOOK_MODE=container.settings.provided.BOT_WEBHOOK_MODE,
                telegram_webhook_url=container.settings.provided.telegram_webhook_url,
                SECRET_KEY=container.settings.provided.SECRET_KEY,
            )

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(
                fastapi_app.state.bot_instance,
                BOT_WEBHOOK_MODE=container.settings.provided.BOT_WEBHOOK_MODE
            )

    return fastapi_app
