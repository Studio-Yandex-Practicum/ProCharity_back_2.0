import datetime
import os

from sqlalchemy.exc import SQLAlchemyError
from telegram.ext import Application

from src.api.constants import DATE_TIME_FORMAT
from src.api.schemas import BotStatus, CommitStatus, DBStatus
from src.core.db.repository import TaskRepository
from src.core.utils import cached_coroutine
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
            bot_status: BotStatus = {"status": False, "error": f"{exc.__class__.__name__}: {exc}"}
            return bot_status
        if settings.BOT_WEBHOOK_MODE:
            method = "webhooks"
            bot_status: BotStatus = {"status": True, "method": method, "url": webhook_info.url}
            return bot_status
        method = "pulling"
        bot_status: BotStatus = {"status": True, "method": method}
        return bot_status

    @cached_coroutine(permanent=True)
    async def get_last_commit(self) -> CommitStatus:
        """В режиме dev - возвращает сведения о последнем коммите, или берет данные из переменных окружения."""
        try:
            from git import Repo

            repo = Repo(os.getcwd())
            master = repo.head.reference
            commit_date = datetime.datetime.fromtimestamp(master.commit.committed_date)
            commit_status: CommitStatus = {
                "last_commit": str(master.commit)[:7],
                "commit_date": commit_date.strftime(DATE_TIME_FORMAT),
                "git_tags": repo.tags,
            }
            return commit_status
        except (ImportError, NameError, TypeError) as exc:
            commit_status: CommitStatus = {
                "last_commit": settings.LAST_COMMIT,
                "commit_date": settings.COMMIT_DATE,
                "git_tags": settings.TAGS,
                "commit_error": f"{exc.__class__.__name__}: {exc}",
            }
            return commit_status

    async def check_db_connection(self) -> DBStatus:
        try:
            active_tasks = await self._repository.count_active_all()
            get_last_update = await self._repository.get_last_update()
        except SQLAlchemyError as exc:
            db_status: DBStatus = {"status": False, "db_connection_error": f"{exc.__class__.__name__}: {exc}"}
            return db_status
        if get_last_update is None:
            get_last_update = "Unable to get last_update"
        db_status: DBStatus = {
            "status": True,
            "last_update": get_last_update,
            "active_tasks": active_tasks,
        }
        return db_status
