import sys
from functools import wraps
from typing import Coroutine

from src.core.db.models import Task
from src.settings import settings

TASK_DEADLINE_FORMAT = "%d.%m.%y"


def display_tasks(task: Task, url: str) -> str:
    deadline = task.deadline.strftime(TASK_DEADLINE_FORMAT)
    bonus_link = f"{url}article/10053"
    return (
        f"<b>{task.title}\n\n</b>"
        f"От фонда: {task.name_organization}\n\n"
        f"Бонусы: <a href='{bonus_link}'>{task.bonus * '💎'}</a>\n"
        f"Категория: {task.category.name}\n"
        f"Срок: {deadline}\n\n"
        f"<a href='{task.link}'>{'Посмотреть задание'}</a>"
    )


def display_task_verbosely(task: Task, url: str) -> str:
    deadline = task.deadline.strftime(TASK_DEADLINE_FORMAT)
    bonus_link = f"{url}article/10053"
    return (
        f"<b>{task.title}\n\n</b>"
        f"От фонда: {task.name_organization}, {task.location}\n\n"
        f"Бонусы: <a href='{bonus_link}'>{task.bonus * '💎'}</a>\n"
        f"Категория: {task.category.name}\n"
        f"Срок: {deadline}\n\n"
        f"{task.description}"
    )


def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self, *args, commit=True):
        result = await func(self, *args)
        if commit:
            await self._session.commit()
        return result

    return auto_commit_wraps


def set_ngrok():
    from pyngrok import ngrok

    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000
    settings.APPLICATION_URL = ngrok.connect(port).public_url


def cached_coroutine(permanent: bool = None, on_each_n: int = None):  # noqa
    """Caches coroutine response permanently or for refreshes it on each N calls"""
    xor_exception = '"permanent" XOR "on_each_n" must be specified'
    if permanent is not None:
        if type(permanent) is not bool:
            raise TypeError('"permanent" must be bool')
        if on_each_n is None:
            if permanent is False:
                raise ValueError(xor_exception)
    if on_each_n is not None:
        if type(on_each_n) is not int:
            raise TypeError('"on_each_n" must be int')
        if on_each_n < 1:
            raise ValueError('"on_each_n" must be positive')
        if permanent is True:
            raise ValueError(xor_exception)

    def wrapped(coroutine: Coroutine):
        result = None
        nonlocal on_each_n
        if on_each_n:
            calls = 0

            async def on_each(*args, **kwargs):
                nonlocal result
                nonlocal calls
                if result is None or calls % on_each_n == 0:
                    result = await coroutine(*args, **kwargs)
                calls = (calls + 1) % on_each_n
                return result

            return on_each

        async def permanent(*args, **kwargs):
            nonlocal result
            if result is None:
                result = await coroutine(*args, **kwargs)
            return result

        return permanent

    return wrapped
