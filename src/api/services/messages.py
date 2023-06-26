from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.bot.bot import create_bot
from src.core.db import get_session
from src.core.db.models import User
from src.core.services.notification import TelegramNotification


class TelegramNotificationService(ContentService):
    """Класс описывающий функционал передачи сообщения
      определенному пользователю """

    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
    ) -> None:
        self._session = session

    async def send_messages_to_group_of_users(self, notifications):
        """ Отправляет сообщение указанной группе пользователей"""
        if notifications.mode == "all":
            users = await self._session.execute(select(User))
        if notifications.mode == "subscribed":
            users = await self._session.execute(select(User).where(User.has_mailing == True)) # noqa
        if notifications.mode == "unsubscribed":
            users = await self._session.execute(select(User).where(User.has_mailing == False)) # noqa

        users = users.scalars().all()
        telegram_notification = TelegramNotification(create_bot())
        await telegram_notification.send_messages(message=notifications.message, users=users)