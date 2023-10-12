from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from telegram.ext import Application

from src.bot import shutdown_bot, startup_bot
from src.core.utils import set_ngrok
from src.depends import Container
from src.settings import Settings


@inject
async def startup(
    fastapi_app: FastAPI,
    run_bot: bool,
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


@inject
async def shutdown(
    fastapi_app: FastAPI,
    run_bot: bool,
    settings: Settings = Provide[Container.settings],
):
    if run_bot:
        await shutdown_bot(
            fastapi_app.state.bot_instance,
            bot_webhook_mode=settings.provided.BOT_WEBHOOK_MODE,
        )
