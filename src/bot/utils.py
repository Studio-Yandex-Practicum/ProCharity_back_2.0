from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from dependency_injector.wiring import Provide
from telegram import Update

from src.core.depends import Container

ReturnType = TypeVar("ReturnType")
ParameterTypes = ParamSpec("ParameterTypes")


def delete_previous_message(
    coroutine: Callable[ParameterTypes, Awaitable[ReturnType]]
) -> Callable[ParameterTypes, Awaitable[ReturnType]]:
    """Декоратор для функций, отправляющих новые сообщения с inline-кнопками.
    После выполнения оборачиваемой функции удаляет сообщение с inline-кнопкой,
    нажатие на которую повлекло вызов оборачиваемой функции."""

    @wraps(coroutine)
    async def wrapper(update: Update, *args: ParameterTypes.args, **kwargs: ParameterTypes.kwargs) -> ReturnType:
        result = await coroutine(update, *args, **kwargs)
        await update.callback_query.message.delete()
        return result

    return wrapper


def get_connection_url(
    telegram_id: int,
    external_id: int = None,
    procharity_url: str = Provide[Container.settings.provided.PROCHARITY_URL],
) -> str:
    """Получение ссылки для связи аккаунта с ботом по external_id и telegram_id.
    В случае отсутствия external_id возвращает ссылку на страницу авторизации"""
    if external_id:
        return f"{procharity_url}auth/bot_procharity.php?user_id={external_id}&telegram_id={telegram_id}"
    return f"{procharity_url}auth/"
