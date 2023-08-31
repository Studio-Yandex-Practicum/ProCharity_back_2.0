import datetime
import os

from git import Repo
from git.exc import InvalidGitRepositoryError
from sqlalchemy.exc import SQLAlchemyError
from telegram.ext import Application

from src.api.constants import DATE_TIME_FORMAT
from src.api.schemas import BotStatus, CommitStatus, DBStatus
from src.core.db.repository import TaskRepository
from src.settings import settings


class HealthCheckService:
    """Сервис для проверки работы бота."""

    def __init__(self, task_repository: TaskRepository, telegram_bot: Application) -> None:
        self._repository = task_repository
        self._bot = telegram_bot

    async def check_bot(self) -> BotStatus:
        try:
            webhook_info = await self._bot.bot.get_webhook_info()
        except Exception as exc:
            bot_status: BotStatus = {"status": False, "error": f"{exc}"}
            return bot_status
        if settings.BOT_WEBHOOK_MODE:
            bot_status: BotStatus = {"status": True, "method": "webhooks", "url": webhook_info.url}
            return bot_status
        bot_status: BotStatus = {"status": True, "method": "pulling"}
        return bot_status

    async def get_last_commit(self) -> CommitStatus:
        try:
            repo = Repo(os.getcwd())
        except InvalidGitRepositoryError as exc:
            commit_status: CommitStatus = {
                "last_commit": f"-",
                "commit_date": f"-",
                "tags": [],
                "commit_error": f"{exc}"
            }
            return commit_status
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
        except SQLAlchemyError as exc:
            db_status: DBStatus = {"status": False, "db_connection_error": f"{exc}"}
            return db_status
        if get_last_update is None:
            get_last_update = 0
        db_status: DBStatus = {
            "status": True,
            "last_update": get_last_update,
            "active_tasks": active_tasks,
        }
        return db_status
