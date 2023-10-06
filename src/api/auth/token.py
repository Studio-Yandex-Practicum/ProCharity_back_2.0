import logging

from fastapi import HTTPException, Request, status

from src.settings import settings


async def check_token(request: Request):
    if not hasattr(settings, "ACCESS_TOKEN_FOR_PROCHARITY"):
        return
    match request.headers.get("token"):
        case None:
            status_code, log_message, message = (
                status.HTTP_401_UNAUTHORIZED,
                "Request without any token provided",
                "Request without token",
            )
        case settings.ACCESS_TOKEN_FOR_PROCHARITY:
            status_code = status.HTTP_200_OK
        case _:
            status_code, log_message, message = (status.HTTP_403_FORBIDDEN, "Token is invalid!", "Token is invalid!")
    logging.info(log_message)
    if status_code == status.HTTP_200_OK:
        return
    raise HTTPException(status_code=status_code, detail=message)
