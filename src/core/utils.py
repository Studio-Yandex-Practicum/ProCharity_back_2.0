import sys
from functools import wraps
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.core.db.models import Task
from src.settings import settings

logger = get_logger()

TASK_DEADLINE_FORMAT = "%d.%m.%y"


class RepositoryProtocol(Protocol):
    _session: AsyncSession


def display_task(task: Task, url: str) -> str:
    deadline = task.deadline.strftime(TASK_DEADLINE_FORMAT) if task.deadline is not None else "Не указан."
    bonus_link = f"{url}article/6646"
    return (
        f"<b>Фонд:</b> {task.name_organization}\n\n"
        f"<b>Категория:</b> {task.category.name if task.category is not None else 'Не указана.'}\n\n"
        f"<b>Срок:</b> {deadline}\n\n"
        f"<b>Бонусы:</b> <a href='{bonus_link}'>{task.bonus * '💎'}</a>\n\n"
        f"<b>{task.title}\n\n</b>"
    )


def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self: RepositoryProtocol, *args, commit=True):
        result = await func(self, *args)
        if commit:
            try:
                await self._session.commit()
            except Exception as e:
                logger.error(e)
                await self._session.rollback()
        return result

    return auto_commit_wraps


def set_ngrok():
    from pyngrok import ngrok

    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000
    settings.APPLICATION_URL = ngrok.connect(port).public_url
