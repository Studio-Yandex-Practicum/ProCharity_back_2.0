import logging

from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import Application

from src.core.db.models import User

logger = logging.getLogger(__name__)


class TelegramNotification:
    def __init__(self, telegram_bot: Application):
        self.__bot_application = telegram_bot
        self.__bot = telegram_bot.bot

    async def send_messages(
        self,
        message: str,
        users: list[User],
        mark_user_for_banned_flag: bool = False,
    ) -> bool:
        """Делает массовую рассылку сообщения message пользователям users.

        Флаг mark_user_for_banned_flag указывает, обновлять ли в объекте модели
        User поле banned, если отправка сообщения была неудачной по причине того,
        что пользователь покинул чат с ботом (признак banned в модели).
        """

        def log_error(exception: TelegramError, user_id: int) -> str:
            msg = f"Ошибка отправки сообщения пользователю {user_id}."
            if type(exception) == BadRequest:
                msg += " Некорректный id?"
            if type(exception) == Forbidden:
                msg += " Бот заблокирован?"
            msg += " " + exception.message
            return msg

        count = 0
        for user in users:
            try:
                await self.__bot.send_message(chat_id=user.telegram_id, text=message)
                logger.debug(f"Отправлено оповещение пользователю {user.telegram_id}")
                count += 1
            except (BadRequest, Forbidden) as exc:
                logger.info(log_error(exc, user.telegram_id))
                if mark_user_for_banned_flag:
                    user.banned = True
        logger.debug(f"Оповещение отправлено в {str(count)} чатов.")
        return True
