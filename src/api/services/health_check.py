import logging

from fastapi import Depends
from telegram.ext import Application

from src.bot.bot import create_bot
from src.settings import settings


class HealthCheckService:
    """Сервис для проверки работы бота."""

    def __init__(
        self,
        telegram_bot: Application = Depends(create_bot),
    ) -> None:
        self._bot: Application = telegram_bot

    async def check_bot(self,) -> dict[str, str]:
        try:
            webhook_info = await self._bot.bot.get_webhook_info()
            logging.info("Health check: Bot connection succeeded")
            if settings.BOT_WEBHOOK_MODE:
                return dict(status="True", method="webhooks", url=webhook_info.url)
            else:
                return dict(status="True", method="pulling")
        except Exception as ex:
            logging.critical(f"Health check: Bot error '{str(ex)}'")
            return dict(status="False", error=f"{ex}")
