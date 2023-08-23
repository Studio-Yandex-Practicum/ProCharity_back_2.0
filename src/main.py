from fastapi import FastAPI

from src.api import init_app
from src.bot import init_bot
from src.bot.bot import shutdown_bot, startup_bot
from src.core.utils import set_ngrok
from src.depends import Container


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
    fastapi_app = init_app(container.fastapi_app())
    bot = init_bot(container.telegram_bot())

    @fastapi_app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        if run_bot:
            fastapi_app.state.bot_instance = await startup_bot(bot)
        if container.settings.provided.USE_NGROK is True:
            set_ngrok()

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(fastapi_app.state.bot_instance)

    return fastapi_app
