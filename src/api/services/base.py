import abc

from fastapi import Depends
from src.core.db.models import Content


class ContentService(abc.ABC):
    """Базовый класс для контента."""

    def __init__(self, repository: any = Depends()):
        self._repository = repository

    async def actualize_objects(self, objects: list[Content]) -> None:
        to_create, to_update = [], []
        await self._repository.set_all_archive_status_true()
        already_have = await self._repository.get_all_non_archived_ids()
        for obj in objects:
            if obj.id not in already_have:
                to_create.append(self._repository._model(**obj.dict(), is_archive=False))
            else:
                to_update.append({**obj.dict(), "is_archive": False})
        if to_create:
            await self._repository.create_all(to_create)
        if to_update:
            await self._repository.update_all(to_update)

    async def get_all(self) -> list[Content]:
        return await self._repository.get_all()
