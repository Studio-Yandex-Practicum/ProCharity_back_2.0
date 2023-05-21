from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class ContentService:
    """Базовый класс для контента."""

    def __init__(self, repository: any = Depends()):
        self._repository = repository

    @asynccontextmanager
    async def get_async_session(self) -> AsyncSession:
        async with AsyncSession() as session:
            yield session

    async def actualize_objects(self, objects: list[any], model_class: any) -> None:
        async with self.get_async_session():
            to_create, to_update = [], []
            await self._repository.archive_all()
            already_have = await self._repository.get_all_ids()
            for obj in objects:
                if obj.id not in already_have:
                    to_create.append(model_class(**obj.dict(), archive=False))
                else:
                    to_update.append({**obj.dict(), "archive": False})
            if to_create:
                await self._repository.create_all(to_create)
            if to_update:
                await self._repository.update_all(to_update)

    async def get_all(self) -> list[any]:
        return await self._repository.get_all()
