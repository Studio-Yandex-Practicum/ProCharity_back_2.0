import abc
from typing import Generic, Sequence, TypeVar

from sqlalchemy import func, select, update
from sqlalchemy.exc import DuplicateColumnError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import desc
from structlog import get_logger

from src.api.constants import DATE_FORMAT_FOR_STATISTICS
from src.core.exceptions import AlreadyExistsException, NotFoundException
from src.core.utils import auto_commit

logger = get_logger()
DatabaseModel = TypeVar("DatabaseModel")
DATE_TIME_FORMAT_LAST_UPDATE = "YYYY-MM-DD HH24:MI:SS"


class AbstractRepository(abc.ABC, Generic[DatabaseModel]):
    """Абстрактный класс, для реализации паттерна Repository."""

    def __init__(self, session: AsyncSession, model: DatabaseModel) -> None:
        self._session = session
        self._model = model

    async def get_or_none(self, _id: int) -> DatabaseModel | None:
        """Получает из базы объект модели по ID. В случае отсутствия возвращает None."""
        return await self._session.scalar(select(self._model).where(self._model.id == _id))

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
        except DuplicateColumnError as exc:
            raise AlreadyExistsException(instance) from exc

        await self._session.refresh(instance)
        return instance

    async def remove(self, instance: DatabaseModel) -> None:
        """Удаляет объект модели из базы данных."""
        await self._session.delete(instance)
        try:
            await self._session.commit()
        except Exception as e:
            logger.error(e)
            await self._session.rollback()

    @auto_commit
    async def update(self, _id: int, instance: DatabaseModel) -> DatabaseModel:
        """Обновляет существующий объект модели в базе."""
        instance.id = _id
        instance = await self._session.merge(instance)
        return instance  # noqa: R504

    @auto_commit
    async def update_all(self, instances: list[dict]) -> Sequence[DatabaseModel]:
        """Обновляет несколько измененных объектов модели в базе."""
        await self._session.execute(update(self._model), instances)
        return instances

    async def get_all(self) -> Sequence[DatabaseModel]:
        """Возвращает все объекты модели из базы данных."""
        objects = await self._session.scalars(select(self._model))
        return objects.all()

    @auto_commit
    async def create_all(self, objects: Sequence[DatabaseModel]) -> None:
        """Создает несколько объектов модели в базе данных."""
        self._session.add_all(objects)

    async def count_all(self) -> int:
        """Возвращает количество объектов модели в базе данных."""
        return await self._session.scalar(select(func.count()).select_from(self._model))

    async def count_active_all(self) -> int:
        """Возвращает количество неархивных (активных) объектов модели в базе данных."""
        return await self._session.scalar(
            select(func.count()).select_from(self._model).where(self._model.is_archived == False)  # noqa
        )

    async def get_last_update(self) -> str | None:
        """Получает из базы отсортированный по времени обновления объект модели.
        В случае отсутствия возвращает None."""
        return await self._session.scalar(
            select(func.to_char(self._model.updated_at, DATE_TIME_FORMAT_LAST_UPDATE)).order_by(
                self._model.updated_at.desc()
            )
        )

    async def get_statistics_by_days(self, date_begin, date_limit, column_name) -> dict[str, int]:
        """Получает из базы отсортированный и отфильтрованный сводный набор записей модели
        по полю column_name.
        """
        column = self._model.__dict__[column_name]
        db_data = await self._session.execute(
            select(func.to_char(column, DATE_FORMAT_FOR_STATISTICS), func.count(column))
            .where(column >= date_begin, column <= date_limit)
            .group_by(column)
            .order_by(column)
        )
        return dict(db_data.fetchall())

    async def get_objects_by_page(
        self, page: int, limit: int, column_name: str = "created_at"
    ) -> Sequence[DatabaseModel]:
        """
        Получает данные, ограниченные параметрами page и limit
        и отсортированные по полю column_name в порядке убывания.
        """
        offset = (page - 1) * limit
        objects = await self._session.scalars(
            (select(self._model).limit(limit).offset(offset).order_by(desc(column_name)))
        )
        return objects.all()


class ContentRepository(AbstractRepository, abc.ABC):
    @auto_commit
    async def archive_by_ids(self, ids: Sequence[int]) -> None:
        """Изменяет is_archived с False на True у не указанных ids."""
        await self._session.execute(
            update(self._model)
            .where(self._model.is_archived == False)  # noqa
            .where(self._model.id.not_in(ids))
            .values({"is_archived": True})
        )

    async def get_by_ids(self, ids: list[int]) -> Sequence[int]:
        """Возвращает id объектов модели из базы данных по указанным ids"""
        filtered_ids = await self._session.scalars(select(self._model.id).where(self._model.id.in_(ids)))
        return filtered_ids.all()

    async def get_by_filter(self, **filter_by) -> Sequence[int]:
        """Возвращает id объектов модели из базы данных по указанному фильтру полей."""
        filtered_ids = await self._session.scalars(select(self._model.id).filter_by(**filter_by))
        return filtered_ids.all()
