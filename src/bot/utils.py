from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from telegram import Update

T = TypeVar("T")
P = ParamSpec("P")


def delete_previous(coroutine: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Для функций, отправляющих сообщения с inline-кнопками.
    Удаляет сообщение с кнопками, приведшее к вызову функции."""

    @wraps(coroutine)
    async def wrapper(update: Update, *args: P.args, **kwargs: P.kwargs) -> T:
        result = await coroutine(update, *args, **kwargs)
        await update.callback_query.message.delete()
        return result

    return wrapper
