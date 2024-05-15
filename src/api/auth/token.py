import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Header

from src.core.depends import Container
from src.core.exceptions import InvalidToken, TokenNotProvided
from src.settings import Settings

log = structlog.get_logger()


@inject
async def check_header_contains_token(
    token: str | None = Header(default=None),
    settings: Settings = Depends(Provide[Container.settings]),
):
    """Проверяем, содержится ли в заголовке запроса token, и сравниваем его
    со значением ACCESS_TOKEN_FOR_PROCAHRITY из settings.py"""

    if not settings.ACCESS_TOKEN_FOR_PROCHARITY:
        await log.awarning(
            "ACCESS_TOKEN_FOR_PROCHARITY не определен, возможны проблемы безопасности. Проверьте настройки проекта."
        )
        return
    match token:
        case None:
            await log.ainfo("В заголовке запроса не содержится токен.")
            raise TokenNotProvided
        case settings.ACCESS_TOKEN_FOR_PROCHARITY:
            return
        case _:
            await log.ainfo("Токен в заголовке запроса неверный.")
            raise InvalidToken
