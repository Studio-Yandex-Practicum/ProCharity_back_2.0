from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import User
from src.core.db.repository.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.__user_repository = UserRepository(session)

    async def register_user(self, telegram_id: int, username: str = "") -> None:
        """Регистрирует нового пользователя по telegram_id.

        Если пользователь найден, обновляет имя и флаг "заблокирован".
        """
        user = await self.__user_repository.get_by_telegram_id(telegram_id)
        if user is not None:
            user_changed = False
            if user.username != username:
                user.username = username
                user_changed = True
            if user.banned:
                user.banned = False
                user_changed = True
            if user_changed:
                await self.__user_repository.update(user.id, user)
            return None
        user = User()
        user.telegram_id = telegram_id
        user.username = username
        await self.__user_repository.create(user)
