from functools import wraps


async def auto_commit(commit=True):  # поставил True временно. Пока не напишется Service
    async def auto_commit_wraps(func):
        @wraps(func)
        async def _wraps(self, *args, **kwargs):
            await func(self, *args, **kwargs)
            if commit is True:
                await self._session.commit()
        return _wraps
    return auto_commit_wraps
