import abc
from typing import TypeVar

from sqlalchemy import select, update, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AlreadyExistsException, NotFoundException

DatabaseModel = TypeVar("DatabaseModel")


class AbstractRepository(abc.ABC):
    """Абстрактный класс, для реализации паттерна Repository."""

    def __init__(self, session: AsyncSession, model: DatabaseModel) -> None:
        self._session = session
        self._model = model

    async def get_or_none(self, _id: int) -> DatabaseModel | None:
        """Получает из базы объект модели по ID. В случае отсутствия возвращает None."""
        db_obj = await self._session.execute(select(self._model).where(self._model.id == _id))
        return db_obj.scalars().first()

    async def get(self, _id: int) -> DatabaseModel:
        """Получает объект модели по ID. В случае отсутствия объекта бросает ошибку."""
        db_obj = await self.get_or_none(_id)
        if db_obj is None:
            raise NotFoundException(object_name=self._model.__name__, object_id=_id)
        return db_obj

    async def create(self, instance: DatabaseModel) -> DatabaseModel:
        """Создает новый объект модели и сохраняет в базе."""
        self._session.add(instance)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            raise AlreadyExistsException(instance) from exc

        await self._session.refresh(instance)
        return instance

    async def update(self, _id: int, instance: DatabaseModel) -> DatabaseModel:
        """Обновляет существующий объект модели в базе."""
        instance.id = _id
        instance = await self._session.merge(instance)
        await self._session.commit()
        return instance  # noqa: R504

    async def update_all(self, instances: list[dict]) -> list[DatabaseModel]:
        """Обновляет несколько измененных объектов модели в базе."""
        await self._session.execute(update(self._model), instances)
        await self._session.commit()
        return instances

    async def get_all(self) -> list[DatabaseModel]:
        """Возвращает все объекты модели из базы данных."""
        objects = await self._session.execute(select(self._model))
        return objects.scalars().all()

    async def create_all(self, objects: list[DatabaseModel]) -> None:
        """Создает несколько объектов модели в базе данных."""
        self._session.add_all(objects)
        await self._session.commit()


class ContentRepository(abc.ABC, AbstractRepository):
    async def archive_all(self) -> None:
        """Добавляет все объекты модели в архив."""
        await self._session.execute(update(self._model).values({"is_archive": True}))
        await self._session.commit()

    async def get_all_ids(self) -> list[int]:
        """Возвращает id всех объектов модели из базы данных."""
        ids = await self._session.execute(select(self._model.id))
        return ids.scalars().all()

    async def get_filtered(self, ids: list[int], is_archived: bool) -> list[DatabaseModel]:
        """Возвращает объекты модели из базы данных, соответствующие указанным фильтрам."""
        objects = await self._session.execute(
            select(self._model).where(
                and_(self._model.id.in_(ids), self._model.is_archive == is_archived)
            )
        )
        return objects.scalars().all()
