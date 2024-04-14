from structlog import get_logger
from telegram import User as TelegramUser

from src.core.db.models import ExternalSiteUser, User, UsersCategories
from src.core.db.repository import ExternalSiteUserRepository, UserRepository
from src.core.logging.utils import logger_decor

logger = get_logger()


class UserService:
    def __init__(self, user_repository: UserRepository, ext_user_repository: ExternalSiteUserRepository) -> None:
        self._user_repository = user_repository
        self._ext_user_repository = ext_user_repository

    async def _update_or_create(self, user: User, **attrs) -> User:
        """Обновляет атрибуты заданного пользователя или создаёт нового,
        если пользователь не задан.
        """
        if user is None:
            return await self._user_repository.create(User(**attrs))

        for attr in attrs:
            setattr(user, attr, attrs[attr])

        return await self._user_repository.update(user.id, user)

    @logger_decor
    async def register_user(
        self,
        ext_site_user: ExternalSiteUser,
        telegram_user: TelegramUser,
    ) -> User:
        """Регистрирует нового пользователя, если он ещё не зарегистрирован."""
        telegram_id = telegram_user.id
        user = await self._user_repository.get_by_external_id(ext_site_user.id)
        user_by_telegram_id = await self._user_repository.get_by_telegram_id(telegram_id)
        do_update_or_create = False
        if user:
            if user.telegram_id != telegram_id:
                await self._update_or_create(user, external_id=None)
                user = user_by_telegram_id
                do_update_or_create = True

        else:
            user = user_by_telegram_id
            do_update_or_create = True

        if do_update_or_create:
            user = await self._update_or_create(
                user,
                telegram_id=telegram_id,
                external_id=ext_site_user.id,
                first_name=ext_site_user.first_name or telegram_user.first_name,
                last_name=ext_site_user.last_name or telegram_user.last_name,
                username=telegram_user.username,
                email=ext_site_user.email,
                role=ext_site_user.role,
            )
            await logger.ainfo(f"Обновлены данные пользователя {user=}")
            if ext_site_user.specializations:
                await self.set_categories_to_user(user.id, ext_site_user.specializations)

        return user

    async def bot_banned(self, user: User) -> None:
        """Обновляет статус User.banned на соответствующий."""
        await self._user_repository.update_bot_banned_status(user, banned=True)

    async def bot_unbanned(self, user: User) -> None:
        """Обновляет статус User.unbanned на соответствующий."""
        await self._user_repository.update_bot_banned_status(user, banned=False)

    async def set_categories_to_user(self, user_id: int, categories_ids: list[int]) -> None:
        """Присваивает пользователю список категорий."""
        await self._user_repository.set_categories_to_user(user_id, categories_ids)

    async def add_category_to_user(self, telegram_id: int, category_id: int) -> None:
        """Добавляет пользователю указанную категорию"""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        await self._user_repository.create(UsersCategories(user_id=user.id, category_id=category_id))

    async def delete_category_from_user(self, telegram_id: int, category_id: int) -> None:
        """Удаляет у пользователя указанную категорию"""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        await self._user_repository.delete_category_from_user(user, category_id)

    async def get_user_categories(self, telegram_id: int, with_archived: bool = False) -> dict[int, str]:
        """Возвращает словарь с id и name категорий пользователя по его telegram_id.
        Если with_archived=True, будут возвращены все категории, включая архивные.
        """
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        categories = await self._user_repository.get_user_categories(user, with_archived)
        return {category.id: category.name for category in categories}

    async def get_user_categories_with_parents(
        self, telegram_id: int, with_archived: bool = False
    ) -> dict[int, dict[int, str]]:
        """Возвращает словарь с id родительской группы словарей с id и name категорий пользователя
        по его telegram_id. Если with_archived=True, будут возвращены все категории, включая архивные."""
        repository = self._user_repository
        user = await repository.get_by_telegram_id(telegram_id)
        categories = await repository.get_user_categories(user, with_archived)
        result = {}
        for category in categories:
            if category.parent_id in result:
                result[category.parent_id].update({category.id: category.name})
            else:
                result[category.parent_id] = {category.id: category.name}
        return result

    async def get_mailing(self, telegram_id: int) -> bool:
        """Возвращает статус подписки пользователя на почтовую рассылку."""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        return user.has_mailing

    async def toggle_mailing(self, telegram_id: int) -> bool:
        """
        Переключает пользователю флаг получения почтовой рассылки на задания.
        Возвращает статус подписки пользователя на почтовую рассылку.
        """
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        await self._user_repository.set_mailing(user, not user.has_mailing)
        return user.has_mailing

    async def check_and_set_has_mailing_atribute(self, telegram_id: int) -> None:
        """
        Присваивает пользователю атрибут has_mailing, для получения почтовой
        рассылки на задания после выбора категорий. Предварительно
        осуществляется проверка, установлен ли этот атрибут у пользователя
        ранее.
        """
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if not user.has_mailing:
            await self._user_repository.set_mailing(user, True)

    async def get_by_telegram_id(self, telegram_id: int) -> User:
        """Оборачивает одноименную функцию из UserRepository."""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        return user

    async def get_by_user_id(self, user_id: int) -> User:
        """Возвращает пользователя (или None) по user_id."""
        user = await self._user_repository.get_by_user_id(user_id)
        return user
