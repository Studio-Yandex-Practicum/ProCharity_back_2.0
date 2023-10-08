import structlog
from fastapi import Request

from src.core.exceptions import InvalidToken, TokenNotProvided
from src.depends import Container

log = structlog.get_logger()


async def check_header_contains_token(request: Request):
    """Проверяем, содержится ли в заголовке запроса token, и сравниваем его
    со значением ACCESS_TOKEN_FOR_PROCAHRITY из settings.py"""
    settings = Container().settings()
    if not hasattr(settings, "ACCESS_TOKEN_FOR_PROCHARITY"):
        await log.awarning(
            "ACCESS_TOKEN_FOR_PROCHARITY не определен, возможны проблемы безопасности. " "Проверьте настройки проекта."
        )
        return
    match request.headers.get("token"):
        case None:
            await log.ainfo("В заголовке запроса не содержится токен.")
            raise TokenNotProvided
        case settings.ACCESS_TOKEN_FOR_PROCHARITY:
            return
        case _:
            await log.info("Токен в заголовке запроса неверный.")
            raise InvalidToken
