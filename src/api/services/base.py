import abc
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repository import ContentRepository


class ContentService(abc.ABC):
    """Абстрактный класс для контента."""

    def __init__(self, repository: ContentRepository, session: AsyncSession):
        self._repository: ContentRepository = repository
        self._session: AsyncSession = session

    async def actualize_objects(
        self,
        objects: list[Any],
        model_class: Any,
        trigger_fields: list[str] | None = None,
    ) -> tuple[list[Any], list[Any]]:
        """Актуализирует объекты в базе данных.

        Args:
            objects: Список pydantic объектов для обновления.
            model_class: Класс соответствующей модели объектов.
            trigger_fields: Список полей, изменение которых считается обновлением объекта.

        Returns:
            Кортеж из двух списков (created_ids, updated_ids)
            created_ids: Список id созданных объектов.
            updated_ids: Список id объектов, у которых произошло изменение хотя бы в одном из
            триггерных полей, заданных trigger_fields
        """
        to_create, to_update, updated_ids = [], [], []
        ids = [obj.id for obj in objects]
        async with self._session as session:
            await self._repository.archive_by_ids(ids, commit=False)
            already_have = await self._repository.get_by_ids(ids)
            for obj in objects:
                obj_dict = obj.dict()
                if obj.id not in already_have:
                    to_create.append(model_class(**obj_dict, is_archived=False))
                else:
                    to_update.append({**obj_dict, "is_archived": False})
                    if trigger_fields:
                        filter = {key: obj_dict[key] for key in trigger_fields if key in obj_dict}
                        if not await self._repository.get_by_filter(id=obj.id, **filter):
                            updated_ids.append(obj.id)
            if to_create:
                await self._repository.create_all(to_create, commit=False)
            if to_update:
                await self._repository.update_all(to_update, commit=False)
            await session.commit()
            return [obj.id for obj in to_create], updated_ids

    async def get_all(self) -> list[Any]:
        return await self._repository.get_all()
