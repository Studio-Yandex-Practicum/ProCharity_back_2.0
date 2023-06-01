import sys
from functools import wraps

from pyngrok import ngrok

from src.core.logging.setup import setup_logging
from src.settings import settings


def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self, *args, commit=True):
        result = await func(self, *args)
        if commit:
            await self._session.commit()
        return result

    return auto_commit_wraps


def set_ngrok():
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000
    public_url = ngrok.connect(port).public_url
    setup_logging()
    settings.APPLICATION_URL = public_url
