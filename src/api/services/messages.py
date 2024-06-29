from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from src.api.schemas import ErrorsSending, InfoRate
from src.core.db.models import Category, ExternalSiteUser, User
from src.core.enums import TelegramNotificationUsersGroups
from src.core.services.notification import TelegramNotification


class TelegramNotificationService:
    """Класс описывающий функционал передачи сообщения
    определенному пользователю"""

    def __init__(
        self,
        session: AsyncSession,
        telegram_notification: TelegramNotification,
    ) -> None:
        self._session = session
        self.telegram_notification = telegram_notification

    async def send_messages_to_group_of_users(self, notifications):
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

    async def send_message_to_user(self, id_hash: str, message: str) -> tuple[bool, str]:
        """Отправляет сообщение пользователю по указанному id_hash"""
        site_user = await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))
        if site_user is None:
            return False, "Пользователь не найден."
        if site_user.user is None:
            return False, "Телеграм пользователя не найден."
        return await self.telegram_notification.send_message(user_id=site_user.user.telegram_id, message=message)

    async def send_message_by_telegram_id(self, telegram_id: int, message: str) -> tuple[bool, str]:
        """Отправляет сообщение пользователю по указанному telegram_id"""
        user = await self._session.scalar(select(User).where(User.telegram_id == telegram_id))
        if user is None:
            return False, "Пользователь не найден."
        return await self.telegram_notification.send_message(user_id=user.telegram_id, message=message)

    async def send_task_to_users_with_category(self, notifications, category_id, reply_markup=None):
        """Отправляет сообщение всем пользователям, подписанным на заданную категорию.

        Args:
            notifications: Текст сообщения.
            category_id: Идентификатор заданной категории, подписчикам на которую отправится сообщение.
            reply_markup: Объект клавиатуры под сообщением рассылки.
        """
        qr = await self._session.scalars(
            select(Category)
            .join(Category.users)
            .options(contains_eager(Category.users))
            .where(User.has_mailing.is_(True) & User.banned.is_(False) & User.external_id.is_not(None))
            .where(Category.id == category_id)
        )
        if (category := qr.first()) is None:
            return
        await self.telegram_notification.send_messages(
            message=notifications, users=category.users, reply_markup=reply_markup
        )

    def count_rate(self, respond: bool, msg: str, rate: InfoRate):
        errors_sending = ErrorsSending()
        if respond:
            rate.successful_rate += 1
            rate.messages.append(msg)
        else:
            rate.unsuccessful_rate += 1
            errors_sending.message = msg
            rate.errors.append(errors_sending)
        return rate

    def collect_respond_and_status(self, result, rate):
        """
        Функция для формирования отчета об отправке
        """
        for res in result:
            rate = self.count_rate(res[0], res[1], rate)
        return rate
