import abc

from fastapi import Depends


class ContentService(abc.ABC):
    """Базовый класс для контента."""

    def __init__(self, repository: any = Depends()):
        self._repository = repository

    async def actualize_objects(self, objects: list[any], model_class: any) -> None:
        to_create, to_update = [], []
        await self._repository.archive_all()
        already_have = await self._repository.get_all_ids()
        for obj in objects:
            if obj.id not in already_have:
                to_create.append(model_class(**obj.dict(), is_archive=False))
            else:
                to_update.append({**obj.dict(), "is_archive": False})
        if to_create:
            await self._repository.create_all(to_create)
        if to_update:
            await self._repository.update_all(to_update)

    async def get_all(self, ids: list[int], is_archived: bool) -> list[any]:
        return await self._repository.get_filtered(ids, is_archived)
