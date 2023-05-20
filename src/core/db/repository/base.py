import abc
from typing import TypeVar
from datetime import datetime

from sqlalchemy import select, update, or_, and_, not_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AlreadyExistsException, NotFoundException
from src.core.utils import auto_commit

from .constants import DATE_FORMAT


CURRENT_DATE = datetime.now().strftime(DATE_FORMAT)

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

    @auto_commit
    async def update(self, _id: int, instance: DatabaseModel) -> DatabaseModel:
        """Обновляет существующий объект модели в базе."""
        instance.id = _id
        instance = await self._session.merge(instance)
        return instance  # noqa: R504

    @auto_commit
    async def update_all(self, instances: list[dict]) -> list[DatabaseModel]:
        """Обновляет несколько измененных объектов модели в базе."""
        await self._session.execute(update(self._model), instances)
        return instances

    async def get_all(self) -> list[DatabaseModel]:
        """Возвращает все объекты модели из базы данных."""
        objects = await self._session.execute(select(self._model))
        return objects.scalars().all()

    @auto_commit
    async def create_all(self, objects: list[DatabaseModel]) -> None:
        """Создает несколько объектов модели в базе данных."""
        self._session.add_all(objects)


class ContentRepository(AbstractRepository, abc.ABC):
    @auto_commit
    async def archive_by_ids(self, ids: list[int]) -> None:
        """Изменяет is_archived с False на True у не указанных ids."""
        await self._session.execute(
            update(self._model)
            .where(self._model.is_archived == False)
            .where(self._model.id.not_in(ids))
            .where(str(self._model.deadline) == CURRENT_DATE)
            .values({"is_archived": True})
        )

    async def get_all_non_archived_and_by_ids(self, ids: list[int]) -> list[int]:
        """Возвращает id всех объектов модели из базы данных, которые не в архиве и по указанным ids"""
        filtred_ids = await self._session.scalars(
            select(self._model.id)
            .where(
                self._model.id.in_(ids)
                | (self._model.is_archived == False)
            )
        )
        return filtred_ids
