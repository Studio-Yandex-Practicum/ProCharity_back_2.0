from src.core.db.models import User, UsersCategories
from src.core.db.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def register_user(
        self,
        telegram_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
        email: str | None = None,
        external_id: int | None = None,
    ) -> User:
        """Регистрирует нового пользователя по telegram_id.

        Если пользователь найден, обновляет имя и флаг "заблокирован".
        """
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if user is None:
            return await self._user_repository.create(
                User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    external_id=external_id,
                )
            )

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.external_id = external_id
        return await self._user_repository.update(user.id, user)

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

    async def get_user_categories(self, telegram_id: int) -> dict[int, str]:
        """Возвращает словарь с id и name категорий пользователя по его telegram_id."""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        categories = await self._user_repository.get_user_categories(user)
        return {category.id: category.name for category in categories}

    async def get_user_categories_with_parents(self, telegram_id: int) -> dict[int, dict[int, str]]:
        """Возвращает словарь с id родительской группы словарей с id и name категорий пользователя
        по его telegram_id."""
        repository = self._user_repository
        user = await repository.get_by_telegram_id(telegram_id)
        categories = await repository.get_user_categories(user)
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

    async def set_mailing(self, telegram_id: int) -> bool:
        """
        Присваивает пользователю получение почтовой рассылки на задания.
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
