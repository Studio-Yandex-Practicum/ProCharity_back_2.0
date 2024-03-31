import sys
from functools import wraps
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.settings import settings

logger = get_logger()


class RepositoryProtocol(Protocol):
    _session: AsyncSession


def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self: RepositoryProtocol, *args, commit=True):
        result = await func(self, *args)
        if commit:
            try:
                await self._session.commit()
            except Exception as e:
                logger.error(e)
                await self._session.rollback()
        return result

    return auto_commit_wraps


def set_ngrok():
    from pyngrok import ngrok

    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000
    settings.APPLICATION_URL = ngrok.connect(port).public_url
