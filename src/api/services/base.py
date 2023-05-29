import abc

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository import ContentRepository


class ContentService(abc.ABC):
    """Абстрактный класс для контента."""

    def __init__(self, repository: ContentRepository, session: AsyncSession):
        self._repository: ContentRepository = repository
        self._session: AsyncSession = session

    async def actualize_objects(self, objects: list[any], model_class: any) -> None:
        to_create, to_update = [], []
        ids = [obj.id for obj in objects]
        async with self._session.begin() as session:
            await self._repository.archive_by_ids(ids, commit=False)
            already_have = await self._repository.get_all_non_archived_and_by_ids(ids)
            for obj in objects:
                if obj.id not in already_have:
                    to_create.append(model_class(**obj.dict(), is_archived=False))
                else:
                    to_update.append({**obj.dict(), "is_archived": False})
            if to_create:
                await self._repository.create_all(to_create, commit=False)
            if to_update:
                await self._repository.update_all(to_update, commit=False)
            await session.commit()

    async def get_all(self) -> list[any]:
        return await self._repository.get_all()
