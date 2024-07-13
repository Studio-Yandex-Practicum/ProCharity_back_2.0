from sqlalchemy import Select, false, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import ExternalSiteUser, Task, TaskResponseVolunteer
from src.core.db.repository.base import AbstractRepository
from src.core.exceptions import NotFoundException
from src.core.utils import auto_commit


class ExternalSiteUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью ExternalSiteUser."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ExternalSiteUser)

    async def get_by_id_hash(self, id_hash: str, with_archived: bool = False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        statement = select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash)
        return await self._session.scalar(self._add_test_not_archived_to_select(statement, not with_archived))

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

    @auto_commit
    async def create_user_response_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Создаёт отклик заданного пользователя на заданную задачу и возвращает True.
        А если такой отклик уже есть в БД, просто возвращает False.
        """
        if not await self.user_responded_to_task(site_user, task):
            response = TaskResponseVolunteer(
                external_site_user_id=site_user.id,
                task_id=task.id,
            )
            self._session.add(response)
            return True

        return False

    @auto_commit
    async def delete_user_response_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Удаляет отклик заданного пользователя на заданную задачу и возвращает True.
        А если такого отклика нет в БД, просто возвращает False.
        """
        response = await self.get_user_response_to_task_or_none(site_user, task)
        if response is not None:
            await self._session.delete(response)
            return True

        return False

    async def get_by_external_id_or_none(
        self, external_id: int, with_archived: bool = False
    ) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по external_id."""
        statement = select(self._model).where(self._model.external_id == external_id)
        return await self._session.scalar(self._add_test_not_archived_to_select(statement, not with_archived))

    async def get_by_external_id(self, external_id: int, with_archived: bool = False) -> ExternalSiteUser:
        """Возвращает пользователя по external_id, а в случае его отсутствия
        возбуждает исключение NotFoundException.
        """
        instance = await self.get_by_external_id_or_none(external_id, with_archived)
        if instance is None:
            raise NotFoundException(object_name=self._model.__name__, external_id=external_id)
        return instance

    async def archive(self, external_id: int) -> None:
        """Архивирует пользователя сайта и удаляет его связь с ботом."""
        instance = await self.get_by_external_id(external_id)
        instance.is_archived = True
        instance.user = None
        await self.update(instance.id, instance)

    def _add_test_not_archived_to_select(self, statement: Select, add_test: bool) -> Select:
        """Добавляет к оператору SELECT проверку условия is_archived = False."""
        return statement.where(self._model.is_archived == false()) if add_test else statement
