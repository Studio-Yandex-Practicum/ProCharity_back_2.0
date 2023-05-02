from functools import wraps


async def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self, objects, commit=True):
        await func(self, objects)
        if commit:
            await self._session.commit()
    return auto_commit_wraps
