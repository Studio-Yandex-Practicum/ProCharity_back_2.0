from dependency_injector.wiring import Provide
from fastapi import FastAPI
from telegram.ext import Application

from src.bot import shutdown_bot, startup_bot
from src.core.utils import set_ngrok
from src.depends import Container
from src.settings import Settings


async def startup(
    run_bot: bool,
    fastapi_app: FastAPI = Provide[Container.fastapi_app],
    bot: Application = Provide[Container.telegram_bot],
    settings: Settings = Provide[Container.settings],
):
    if settings.USE_NGROK is True:
        set_ngrok()
    if run_bot:
        fastapi_app.state.bot_instance = await startup_bot(
            bot=bot,
            bot_webhook_mode=settings.BOT_WEBHOOK_MODE,
            telegram_webhook_url=settings.telegram_webhook_url,
            secret_key=settings.SECRET_KEY,
        )


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
    fastapi_app = container.fastapi_app()

    @fastapi_app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        await startup(run_bot)

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(
                fastapi_app.state.bot_instance, bot_webhook_mode=container.settings.provided.BOT_WEBHOOK_MODE
            )

    return fastapi_app
