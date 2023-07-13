from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import structlog

T = TypeVar("T")
P = ParamSpec("P")

log = structlog.get_logger()


async def logging_updates(*args, **kwargs):
    await log.ainfo("Следующие Updates не были пойманы ни одним из обработчиков", args=args, kwargs=kwargs)


def logger_decor(coroutine: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    @wraps(coroutine)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        await log.ainfo(
            f"Запущенна функция {coroutine.__name__}",
            args=args,
            kwargs=kwargs,
        )
        return await coroutine(*args, **kwargs)

    return wrapper
