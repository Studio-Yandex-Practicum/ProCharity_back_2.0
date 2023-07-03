import asyncio
import logging

from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import Application

from src.core.db.models import User

logger = logging.getLogger(__name__)


class TelegramNotification:
    def __init__(self, telegram_bot: Application):
        self.__bot_application = telegram_bot
        self.__bot = telegram_bot.bot

    async def __send_message(self, user_id: int, message: str) -> None:
        try:
            await self.__bot.send_message(chat_id=user_id, text=message)
            logger.debug(f"Отправлено оповещение пользователю {user_id}")
        except TelegramError as exc:
            msg = f"Ошибка отправки сообщения пользователю {user_id}."
            match exc:
                case BadRequest():
                    msg += " Некорректный id?"
                case Forbidden():
                    msg += " Бот заблокирован?"
            msg += " " + exc.message
            logger.info(msg)

    async def send_messages(
        self,
        message: str,
        users: list[User],
    ) -> bool:
        """Делает массовую рассылку сообщения message пользователям users."""
        send_message_tasks = (self.__send_message(user.telegram_id, message) for user in users)
        self.__bot_application.create_task(asyncio.gather(*send_message_tasks))
        return True

    async def send_message(
        self,
        message: str,
        user_id: int,
    ) -> bool:
        """Отправляет сообщение message конкретному пользователю user."""
        await self.__send_message(user_id, message)
        return True
