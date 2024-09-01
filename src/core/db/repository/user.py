from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, and_, delete, desc, func, insert, or_, orm, select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.core.db.models import ExternalSiteUser, User, UsersCategories
from src.core.db.repository.base import FilterableRepository
from src.core.enums import UserRoleFilterValues, UserStatusFilterValues
from src.core.utils import auto_commit

logger = get_logger()


class UserRepository(FilterableRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    @auto_commit
    async def get_by_user_id(self, user_id: int) -> User | None:
        """Возвращает пользователя (или None) по user_id."""
        return await self._session.scalar(select(User).where(User.id == user_id))

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Возвращает пользователя (или None) по telegram_id."""
        return await self._session.scalar(
            select(User).options(orm.selectinload(User.external_user)).where(User.telegram_id == telegram_id)
        )

    async def get_by_external_id(self, external_id: int) -> User | None:
        """Возвращает пользователя (или None) по external_id."""
        return await self._session.scalar(select(User).where(User.external_id == external_id))

    async def restore_existing_user(
        self, user: User, username: str, first_name: str, last_name: str, external_id: int | None
    ) -> User:
        """Обновляет данные пользователя, который уже был в базе.

        Если ранее существовавший юзер делает /start в боте, то проверяются/обновляются его username, first_name,
        last_name и сбрасывается флаг "banned" - признак, что бот у него был заблокирован.
        """
        if (
            user.username != username
            or user.first_name != first_name
            or user.last_name != last_name
            or user.banned
            or user.external_id != external_id
        ):
            user.username, user.first_name, user.last_name, user.banned, external_id = (
                username,
                first_name,
                last_name,
                False,
                external_id or user.external_id,
            )
            await self.update(user.id, user)
        return user

    async def update_bot_banned_status(self, user: User, banned: bool) -> None:
        """Обновляем статус User.banned на соответствующий."""
        user.banned = banned
        await self.update(user.id, user)

    async def set_categories_to_user(self, user_id: int, categories_ids: list[int] | None) -> None:
        """Присваивает или удаляет список категорий."""
        await self._session.commit()
        async with self._session.begin():
            await self._session.execute(delete(UsersCategories).where(UsersCategories.user_id == user_id))
            if categories_ids:
                await self._session.execute(
                    insert(UsersCategories).values(
                        [{"user_id": user_id, "category_id": category_id} for category_id in categories_ids]
                    )
                )
        await logger.ainfo("Изменены категории у пользователя")

    @auto_commit
    async def delete_category_from_user(self, user: User, category_id: int) -> None:
        """Удаляет категорию у пользователя."""
        await self._session.execute(
            delete(UsersCategories)
            .where(UsersCategories.user_id == user.id)
            .where(UsersCategories.category_id == category_id)
        )

    async def set_mailing(self, user: User, has_mailing: bool) -> None:
        """
        Присваивает пользователю статус получения
        почтовой рассылки на задания.
        """
        user.has_mailing = has_mailing
        await self.update(user.id, user)

    def _add_filter_by_role_to_select(self, statement: Select, role: str | None) -> Select:
        """Добавляет к оператору SELECT проверку значения в поле role."""
        if role == str(UserRoleFilterValues.UNKNOWN):
            return statement.where(User.role.is_(None))
        if role is not None:
            return statement.where(User.role == role)
        return statement

    def _add_filter_by_external_id_to_select(self, statement: Select, external_id_exists: bool | None) -> Select:
        """Добавляет к оператору SELECT проверку привязки к external_site_users в поле external_id."""
        if external_id_exists is True:
            return statement.where(User.external_id.is_not(None))
        if external_id_exists is False:
            return statement.where(User.external_id.is_(None))
        return statement

    def _add_filter_by_moderation_status(self, statement: Select, status: str | None) -> Select:
        """Добавляет к оператору SELECT проверку статуса external_site_users.moderation_status."""
        if status == UserStatusFilterValues.UNKNOWN:
            return statement.where(or_(ExternalSiteUser.id.is_(None), ExternalSiteUser.moderation_status.is_(None)))
        if status is not None:
            return statement.where(and_(ExternalSiteUser.id.is_not(None), ExternalSiteUser.moderation_status == status))
        return statement

    def apply_filter(self, statement: Select, filter_by: dict[str, Any]) -> Select:
        """Применяет фильтрацию по заданным в filter_by полям."""
        filter_select_updaters = {
            "role": self._add_filter_by_role_to_select,
            "authorization": self._add_filter_by_external_id_to_select,
            "status": self._add_filter_by_moderation_status,
        }
        for filter_field, executor in filter_select_updaters.items():
            statement = executor(statement, filter_by.get(filter_field))
        return statement

    async def count_by_filter(self, filter_by: dict[str, Any]) -> int:
        """Возвращает количество записей, удовлетворяющих фильтру"""
        statement = select(func.count()).select_from(User).join(User.external_user, isouter=True)
        statement = self.apply_filter(statement, filter_by)
        return await self._session.scalar(statement)

    async def get_filtered_objects_by_page(
        self, filter_by: dict[str, Any], page: int, limit: int, column_name: str = "created_at"
    ) -> Sequence[User]:
        """
        Получает отфильтрованные данные, ограниченные параметрами page и limit
        и отсортированные по полю column_name в порядке убывания.
        """
        statement = self.apply_filter(
            select(User).join(User.external_user, isouter=True),
            filter_by,
        )
        if page > 0:
            offset = (page - 1) * limit
            statement = statement.limit(limit).offset(offset)

        objects = await self._session.scalars(statement.order_by(desc(column_name)))
        return objects.all()
