from functools import wraps


async def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self, commit=True, *args, **kwargs):
        if commit:
            await self._session.commit()
        return await func(*args, **kwargs)
    return auto_commit_wraps
