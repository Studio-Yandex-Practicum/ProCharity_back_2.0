import datetime
#import logging
import os

from fastapi import Depends
from git import Repo
from sqlalchemy.exc import SQLAlchemyError
from telegram.ext import Application

from src.api.constants import DATE_TIME_FORMAT
from src.api.schemas import BotStatus, CommitStatus, DBStatus, HealthCheck
from src.bot.bot import create_bot
from src.core.db.repository import TaskRepository
from src.settings import settings


class HealthCheckService:
    """Сервис для проверки работы бота."""

    def __init__(
        self,
        telegram_bot: Application = Depends(create_bot),
        task_repository: TaskRepository = Depends(),
    ) -> None:
        self._bot: Application = telegram_bot
        self._repository: TaskRepository = task_repository

    async def check_bot(self) -> BotStatus:
        try:
            webhook_info = await self._bot.bot.get_webhook_info()
            #logging.info("Health check: Bot connection succeeded")
            if settings.BOT_WEBHOOK_MODE:
                bot_status: BotStatus = {"status": True, "method": "webhooks", "url": webhook_info.url}
                return bot_status
            else:
                bot_status: BotStatus = {"status": True, "method": "pulling"}
                return bot_status
        except Exception as exc:
            # logging.critical(f"Health check: Bot error '{str(exc)}'")
            bot_status: BotStatus = {"status": False, "error": f"{exc}"}
            return bot_status

    async def get_last_commit(self) -> CommitStatus:
        repo = Repo(os.getcwd())
        master = repo.head.reference
        commit_date = datetime.datetime.fromtimestamp(master.commit.committed_date)
        commit_status: CommitStatus = {
            "last_commit": str(master.commit)[:7],
            "commit_date": commit_date.strftime(DATE_TIME_FORMAT),
            "tags": repo.tags,
        }
        return commit_status

    async def check_db_connection(self) -> DBStatus:
        try:
            active_tasks = await self._repository.count_active_all()
            get_last_update = await self._repository.get_last_update()
            if get_last_update is None:
                get_last_update = 0
            # logging.info("Health check: Database connection succeeded")
            db_status: DBStatus = {
                "status": True,
                "last_update": get_last_update,
                "active_tasks": active_tasks,
            }
            return db_status
        except SQLAlchemyError as exc:  #TODO Если остановить контейнер, все падает с 500й ошибкой. Ловли искл. нет!!!
            # logging.critical(f"Health check: Database error '{str(exc)}'")
            db_status: DBStatus = {"status": False, "db_connection_error": f"{exc}"}
            return db_status
