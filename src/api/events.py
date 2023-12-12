from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from telegram.ext import Application

from src.bot import shutdown_bot, startup_bot
from src.core.depends import Container
from src.core.utils import set_ngrok
from src.settings import Settings


@inject
async def startup(
    fastapi_app: FastAPI,
    run_bot: bool,
    bot: Application = Provide[Container.applications_container.telegram_bot],
    settings: Settings = Provide[Container.settings],
):
    if settings.USE_NGROK is True:
        set_ngrok()
    if run_bot:
        fastapi_app.state.bot_instance = await startup_bot(
            bot=bot,
            bot_webhook_mode=settings.BOT_WEBHOOK_MODE,
            telegram_webhook_url=settings.telegram_webhook_url,
            telegram_secret_token=settings.TELEGRAM_SECRET_TOKEN,
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
            bot_webhook_mode=settings.BOT_WEBHOOK_MODE,
        )
