from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, desc, false, func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import TechMessage
from src.core.db.repository.base import ArchivableRepository


class TechMessageRepository(ArchivableRepository):
    """Репозиторий для работы с моделью TechMessage."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TechMessage)

    async def partial_update(self, id: int, data: dict) -> TechMessage:
        """Обновляет данные/часть данных технического сообщения."""
        tech_message = await self.get(id)

        for attr, value in data.items():
            setattr(tech_message, attr, value)

        return await self.update(id, tech_message)

    def _add_filter_by_was_read(self, statement: Select, was_read: bool | None) -> Select:
        """Добавляет к оператору SELECT проверку статуса технического сообщения (was_read)."""
        if was_read is True:
            return statement.where(TechMessage.was_read == true())
        elif was_read is False:
            return statement.where(TechMessage.was_read == false())
        return statement

    async def count_by_filter(self, filter_by: dict) -> int:
        """Возвращает количество не архивных данных, удовлетворяющих фильтру."""
        statement = self._add_filter_by_was_read(
            select(func.count()).select_from(TechMessage),
            filter_by.get("was_read"),
        )
        return await self._session.scalar(statement.where(TechMessage.is_archived == false()))

    async def get_filtered_tech_messages_by_page(
        self, filter_by: dict[str:Any], page: int, limit: int, column_name: str = "created_at"
    ) -> Sequence[TechMessage]:
        """
        Получает отфильтрованные не архивные данные, ограниченные параметрами page и limit
        и отсортированные по полю column_name в порядке убывания.
        """
        offset = (page - 1) * limit
        statement = self._add_filter_by_was_read(
            select(TechMessage),
            filter_by.get("was_read"),
        )
        objects = await self._session.scalars(
            statement.where(TechMessage.is_archived == false()).limit(limit).offset(offset).order_by(desc(column_name))
        )
        return objects.all()
