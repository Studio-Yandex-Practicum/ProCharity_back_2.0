from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

import structlog

ReturnType = TypeVar("ReturnType")
ParameterTypes = ParamSpec("ParameterTypes")

log = structlog.get_logger()


async def logging_updates(*args, **kwargs):
    await log.ainfo("Следующие Updates не были пойманы ни одним из обработчиков", args=args, kwargs=kwargs)


def logger_decor(
    coroutine: Callable[ParameterTypes, Awaitable[ReturnType]]
) -> Callable[ParameterTypes, Awaitable[ReturnType]]:
    
    @wraps(coroutine)
    async def wrapper(
        *args: ParameterTypes.args,
        **kwargs: ParameterTypes.kwargs
    ) -> ReturnType:
        await log.ainfo(
            f"Запущенна функция {coroutine.__name__}",
            args=args,
            kwargs=kwargs,
        )
        return await coroutine(*args, **kwargs)

    return wrapper
