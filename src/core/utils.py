async def auto_commit(func):
    async def auto_commit_wraps(self, commit=True):
        if commit:
            await self._session.commit()
    return auto_commit_wraps
