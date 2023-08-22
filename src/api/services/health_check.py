import datetime
import logging
import os

from fastapi import Depends
from git import Repo
from telegram.ext import Application
from typing import Union

from src.api.constants import DATE_TIME_FORMAT
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


    async def get_last_commit(self,) -> dict[str, Union[str, list[str]]]:
        repo = Repo(os.getcwd())
        master = repo.head.reference
        commit_date = datetime.datetime.fromtimestamp(master.commit.committed_date)
        last_commit = dict(last_commit=str(master.commit)[:7],
                      commit_date=commit_date.strftime(DATE_TIME_FORMAT),
                      tags=repo.tags)
        return last_commit
