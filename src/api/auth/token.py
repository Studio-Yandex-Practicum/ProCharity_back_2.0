import logging

from fastapi import HTTPException, Request, status

from src import settings


async def check_token(request: Request):
    if not hasattr(settings, "ACCESS_TOKEN_FOR_PROCHARITY"):
        return True
    if not request.headers.__contains__("token"):
        logging.info("Request without any token provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Request without token")
    token = request.headers["token"]
    if token != settings.ACCESS_TOKEN_FOR_PROCHARITY:
        logging.info("Token is invalid!")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is invalid!")
    return True
