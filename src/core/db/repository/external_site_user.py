from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import ExternalSiteUser, Task, TaskResponseVolunteer
from src.core.db.repository.base import AbstractRepository


class ExternalSiteUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью ExternalSiteUser."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ExternalSiteUser)

    async def get_by_id_hash(self, id_hash: str) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        return await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))

    async def get_or_create_by_id_hash(self, id_hash: str) -> tuple[ExternalSiteUser, bool]:
        """Возвращает или создает пользователя по id_hash."""
        instance = await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))
        if instance is not None:
            return (instance, False)
        return await self.create(ExternalSiteUser(id_hash=id_hash)), True

    async def get_user_response_to_task_or_none(
        self, site_user: ExternalSiteUser, task: Task
    ) -> TaskResponseVolunteer | None:
        """Возвращает отклик заданного пользователя на заданную задачу, если такой
        отклик есть в БД, иначе возвращает None.
        """
        return await self._session.scalar(
            select(TaskResponseVolunteer)
            .where(TaskResponseVolunteer.external_site_user_id == site_user.id)
            .where(TaskResponseVolunteer.task_id == task.id)
        )

    async def user_responded_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Возвращает True, если в БД имеется отклик заданного пользователя
        на заданную задачу, иначе False.
        """
        return await self.get_user_response_to_task_or_none(site_user, task) is not None

    async def create_user_response_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Создаёт отклик заданного пользователя на заданную задачу и возвращает True,
        если такого отклика ещё нет в БД, иначе просто возвращает False.
        """
        await self._session.commit()
        async with self._session.begin():
            if not await self.user_responded_to_task(site_user, task):
                response = TaskResponseVolunteer(
                    external_site_user_id=site_user.id,
                    task_id=task.id,
                )
                self._session.add(response)
                return True

            return False

    async def delete_user_response_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Удаляет отклик заданного пользователя на заданную задачу и возвращает True,
        если такой отклик есть в БД, иначе просто возвращает False.
        """
        await self._session.commit()
        async with self._session.begin():
            response = await self.get_user_response_to_task_or_none(site_user, task)
            if response is not None:
                await self._session.delete(response)
                return True

            return False
