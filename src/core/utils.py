from functools import wraps


async def auto_commit(func):
    @wraps(func)
    async def auto_commit_wraps(self, commit=True):
        if commit:
            await self._session.commit()
        return func
    return auto_commit_wraps
