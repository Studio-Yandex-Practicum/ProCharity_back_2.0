import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from telegram.ext import Application

from src.api.schemas import ErrorsSending, InfoRate
from src.core.db.models import Category, User
from src.core.enums import TelegramNotificationUsersGroups
from src.core.exceptions.exceptions import SendMessageError
from src.core.services.notification import TelegramNotification

log = structlog.get_logger(module=__name__)


class TelegramNotificationService:
    """Класс описывающий функционал передачи сообщения
    определенному пользователю"""

    def __init__(
        self,
        telegram_bot: Application,
        session: AsyncSession,
    ) -> None:
        self._session = session
        self.telegram_notification = TelegramNotification(telegram_bot)

    async def send_messages_to_group_of_users(self, notifications):
        """Отправляет сообщение указанной группе пользователей"""
        match notifications.mode.upper():
            case TelegramNotificationUsersGroups.ALL.name:
                users = await self._session.scalars(select(User))
            case TelegramNotificationUsersGroups.SUBSCRIBED.name:
                users = await self._session.scalars(select(User).where(User.has_mailing == True))  # noqa
            case TelegramNotificationUsersGroups.UNSUBSCRIBED.name:
                users = await self._session.scalars(select(User).where(User.has_mailing == False))  # noqa
        return await self.telegram_notification.send_messages(message=notifications.message, users=users)

    async def send_message_to_user(self, telegram_id, notifications):
        """Отправляет сообщение указанному по telegram_id пользователю"""
        return await self.telegram_notification.send_message(user_id=telegram_id, message=notifications.message)

    async def send_message_to_user_by_id(self, user_id, notifications) -> tuple[bool, str]:
        """Отправляет сообщение указанному пользователю по user_id."""
        try:
            user_i: User | None = await self._session.scalar(select(User).where(User.id == user_id))
            if not user_i:
                """Пользователь не найден."""
                raise SendMessageError(user_id, "Unable to find the user")
            if not user_i.telegram_id:
                """Telegram_id не найден."""
                raise SendMessageError(user_id, "Unable to find telegram_id for this user")
            if user_i.banned:
                """Пользователь отписался от уведомлений."""
                raise SendMessageError(user_id, "User blocked the bot")
            return await self.telegram_notification.send_message(
                user_id=user_i.telegram_id, message=notifications.message
            )
        except SendMessageError as e:
            await log.ainfo(e)
            return False, str(e)

    async def send_messages_to_subscribed_users(self, notifications, category_id):
        """Отправляет сообщение пользователям, подписанным на определенные категории"""
        category = await self._session.scalars(
            select(Category).options(joinedload(Category.users)).where(Category.id == category_id)
        )
        category = category.first()
        await self.telegram_notification.send_messages(message=notifications, users=category.users)

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
