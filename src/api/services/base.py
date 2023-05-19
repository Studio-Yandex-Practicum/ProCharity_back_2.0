from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import CategoryRequest, TaskRequest
from src.core.db.db import get_session


class ContentService:
    """Базовый класс для контента."""

    def __init__(self, repository: any = Depends(), session: AsyncSession = Depends(get_session)):
        self._repository = repository
        self._session = session

    async def actualize_objects(self, objects: list[CategoryRequest | TaskRequest], model_class: any) -> None:
        to_create, to_update = [], []
        with self._session.begin() as session:
            await self._repository.archive_all(commit=False)
            already_have = await self._repository.get_all_ids()
            for obj in objects:
                if obj.id not in already_have:
                    to_create.append(model_class(**obj.dict(), archive=False))
                else:
                    to_update.append({**obj.dict(), "archive": False})
            if to_create:
                await self._repository.create_all(to_create, commit=False)
            if to_update:
                await self._repository.update_all(to_update, commit=False)
            session.commit()

    async def get_all(self) -> list[any]:
        return await self._repository.get_all()
