from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from telegram import Update

ReturnType = TypeVar("ReturnType")
ParameterTypes = ParamSpec("ParameterTypes")


def delete_previous(
    coroutine: Callable[ParameterTypes, Awaitable[ReturnType]]
) -> Callable[ParameterTypes, Awaitable[ReturnType]]:
    """Декоратор для функций, отправляющих новые сообщения с inline-кнопками.
    После выполнения оборачиваемой функции удаляет сообщение с inline-кнопкой,
    нажатие на которую повлекло вызов оборачиваемой функции."""

    @wraps(coroutine)
    async def wrapper(
        update: Update,
        *args: ParameterTypes.args,
        **kwargs: ParameterTypes.kwargs
    ) -> ReturnType:
        result = await coroutine(update, *args, **kwargs)
        await update.callback_query.message.delete()
        return result

    return wrapper
