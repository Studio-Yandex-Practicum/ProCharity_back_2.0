from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from src.api.schemas import TelegramNotificationUsersRequest
from src.core.db.models import Category, ExternalSiteUser, User
from src.core.enums import TelegramNotificationUsersGroups
from src.core.services.notification import TelegramMessageTemplate, TelegramNotification


class TelegramNotificationService:
    """Класс, описывающий функционал передачи сообщения
    определенному пользователю"""

    def __init__(
        self,
        session: AsyncSession,
        telegram_notification: TelegramNotification,
    ) -> None:
        self._session = session
        self.telegram_notification = telegram_notification

    async def send_messages_to_filtered_users(
        self, notifications: TelegramNotificationUsersRequest
    ) -> list[tuple[bool, str]]:
        """Отправляет сообщение указанной группе пользователей"""
        match notifications.mode.upper():
            case TelegramNotificationUsersGroups.ALL.name:
                users = await self._session.scalars(select(User).where(User.banned.is_(False)))
            case TelegramNotificationUsersGroups.SUBSCRIBED.name:
                users = await self._session.scalars(
                    select(User).where(User.has_mailing.is_(True) & User.banned.is_(False))
                )
            case TelegramNotificationUsersGroups.UNSUBSCRIBED.name:
                users = await self._session.scalars(
                    select(User).where(User.has_mailing.is_(False) & User.banned.is_(False))
                )
        return await self.telegram_notification.send_messages(message=notifications.message, users=users)

    async def send_message_to_user_by_id_hash(self, id_hash: str, message: str) -> tuple[bool, str]:
        """Отправляет сообщение пользователю по указанному id_hash"""
        site_user = await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))
        if site_user is None:
            return False, "Пользователь не найден."
        if site_user.user is None:
            return False, "Телеграм пользователя не найден."
        return await self.telegram_notification.send_message(telegram_id=site_user.user.telegram_id, message=message)

    async def send_message_by_telegram_id(self, telegram_id: int, message: str) -> tuple[bool, str]:
        """Отправляет сообщение пользователю по указанному telegram_id"""
        user = await self._session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            return False, "Пользователь не найден."
        return await self.telegram_notification.send_message(telegram_id=user.telegram_id, message=message)

    async def send_task_to_users_with_category(self, category_id: int, template: TelegramMessageTemplate):
        """Отправляет задание всем зарегистрированным пользователям, подписанным на заданную категорию.

        Args:
            category_id: идентификатор категории, подписчикам которой отправится сообщение;
            template: шаблон сообщения.
        """
        qr = await self._session.scalars(
            select(Category)
            .join(Category.users)
            .join(User.external_user)
            .options(contains_eager(Category.users).contains_eager(User.external_user))
            .where(User.external_user is not None)
            .where(User.has_mailing.is_(True) & User.banned.is_(False))
            .where(Category.id == category_id)
        )
        if (category := qr.first()) is None:
            return
        await self.telegram_notification.send_messages_by_template(category.users, template)
