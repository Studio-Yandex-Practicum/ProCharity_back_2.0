from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from telegram.ext import Application

from src.bot import shutdown_bot, startup_bot
from src.core.depends import Container
from src.core.utils import set_ngrok


@inject
async def startup(
    fastapi_app: FastAPI,
    run_bot: bool,
    bot: Application = Provide[Container.applications_container.telegram_bot],
    use_ngrok: bool = Provide[Container.settings.provided.USE_NGROK],
    bot_webhook_mode: bool = Provide[Container.settings.provided.BOT_WEBHOOK_MODE],
    telegram_webhook_url: str = Provide[Container.settings.provided.telegram_webhook_url],
    telegram_secret_token: str = Provide[Container.settings.provided.TELEGRAM_SECRET_TOKEN],
):
    if use_ngrok is True:
        set_ngrok()
    if run_bot:
        fastapi_app.state.bot_instance = await startup_bot(
            bot=bot,
            bot_webhook_mode=bot_webhook_mode,
            telegram_webhook_url=telegram_webhook_url,
            telegram_secret_token=telegram_secret_token,
        )


@inject
async def shutdown(
    fastapi_app: FastAPI,
    run_bot: bool,
    bot_webhook_mode: str = Provide[Container.settings.provided.BOT_WEBHOOK_MODE],
):
    if run_bot:
        await shutdown_bot(
            fastapi_app.state.bot_instance,
            bot_webhook_mode=bot_webhook_mode,
        )
