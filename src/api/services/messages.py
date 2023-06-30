from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from telegram.ext import Application

from src.bot.bot import create_bot
from src.core.db import get_session
from src.core.db.models import User
from src.core.enums import TelegramNotificationUsersGroups
from src.core.services.notification import TelegramNotification


class TelegramNotificationService:
    """Класс описывающий функционал передачи сообщения
    определенному пользователю"""

    def __init__(
        self,
        telegram_bot: Application = Depends(create_bot),
        session: AsyncSession = Depends(get_session),
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
        await self.telegram_notification.send_messages(message=notifications.message, users=users)

    async def send_message_to_user(self, telegram_id, notifications):
        """Отправляет сообщение указанному по telegram_id пользователю"""
        await self.telegram_notification._TelegramNotification__send_message(
            user_id=telegram_id, message=notifications.message
        )
