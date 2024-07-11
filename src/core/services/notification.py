import asyncio

import structlog
from telegram import TelegramObject
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import Application

from src.core.db.models import User

log = structlog.get_logger(module=__name__)


class TelegramMessageTemplate:
    """Базовый класс шаблонов телеграм-сообщений."""

    async def render(user: User) -> dict:
        """Возвращает словарь с атрибутами телеграм-сообщения, предназначенного
        для заданного пользователя.
        Ключи словаря соответствуют параметрам функции Bot.send_message().
        """
        raise NotImplementedError


class TelegramNotification:
    def __init__(self, telegram_bot: Application):
        self.__bot_application = telegram_bot
        self.__bot = telegram_bot.bot

    async def __send_message(
        self,
        user_id: int,
        text: str,
        reply_markup: TelegramObject | None = None,
    ) -> tuple[bool, str]:
        try:
            await self.__bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=reply_markup,
            )
            msg = f"Отправлено оповещение пользователю {user_id}"
            await log.adebug(msg)
            return True, msg
        except TelegramError as exc:
            msg = f"Ошибка отправки сообщения пользователю {user_id}."
            match exc:
                case BadRequest():
                    msg += " Некорректный id."
                case Forbidden():
                    msg += " Бот заблокирован."
            msg += " " + exc.message
            await log.ainfo(msg)
            return False, msg

    async def send_messages(
        self,
        message: str,
        users: list[User],
        reply_markup: TelegramObject | None = None,
    ) -> list[tuple[bool, str]]:
        """Делает массовую рассылку сообщения message пользователям users."""
        send_message_tasks = [self.__send_message(user.telegram_id, message, reply_markup) for user in users]
        result = await asyncio.gather(*send_message_tasks)
        return result

    async def send_messages_by_template(
        self,
        users: list[User],
        template: TelegramMessageTemplate,
    ) -> list[tuple[bool, str]]:
        """Отправляет пользователям users сообщения на основе шаблона template."""
        send_message_tasks = [self.__send_message(user.telegram_id, **(await template.render(user))) for user in users]
        return await asyncio.gather(*send_message_tasks)

    async def send_message(
        self,
        message: str,
        user_id: int,
        reply_markup: TelegramObject | None = None,
    ) -> tuple[bool, str]:
        """Отправляет сообщение message конкретному пользователю user."""
        return await self.__send_message(user_id, message, reply_markup)
