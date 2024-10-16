import aiohttp
from structlog import get_logger

from src.bot.constants.enum import CANCEL_RESPOND_REASONS
from src.core.db.models import User
from src.core.enums import UserResponseAction
from src.core.schemas.procharity_api import (
    SiteBotRespondRequest,
    SiteBotStatusFundRequest,
    SiteBotStatusVolunteerRequest,
    SiteUserCategoriesRequest,
)
from src.settings import Settings

from .email import EmailProvider
from .tech_message import TechMessageService

logger = get_logger(module=__name__)


class ProcharityAPI:
    """Сервис для отправки сообщений на сайт."""

    def __init__(self, settings: Settings, email_provider: EmailProvider, tech_message_service: TechMessageService):
        self._settings = settings
        self._email_provider = email_provider
        self._tech_message_service = tech_message_service

    @property
    def token_header_dict(self) -> dict[str, str]:
        """Возвращает заголовок с токеном авторизации в виде словаря."""
        return {"token": self._settings.ACCESS_TOKEN_SEND_DATA_TO_PROCHARITY}

    async def _site_post(self, url: str, data: str, user_id: int, log_description: str) -> bool:
        """Осуществляет post запрос на заданный url сайта.

        Args:
            url: Адрес запроса.
            data: Данные запроса.
            user_id: Идентификатор пользователя (для логирования).
            log_description: Описание запроса (для логирования).
        Return:
            True: отправка выполнена успешно;
            False: отправка выполнена неуспешно.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=data, headers=self.token_header_dict) as response:
                    data = await response.json()
                    if response.status != 200:
                        await self._notify_of_data_transfer_error(
                            user_id, log_description, f"status = {response.status}, message = {data}"
                        )
                        return False
                    else:
                        await logger.adebug(
                            f"Успешная передача данных на сайт: {log_description} пользователя {user_id}. Ответ: {data}"
                        )
                        return True
        except aiohttp.ClientResponseError as e:
            await self._notify_of_data_transfer_error(
                user_id, log_description, f"Неверный ответ от сайта ({e.message})."
            )
        except Exception as e:
            await logger.aexception(e)

        return False

    async def _notify_of_data_transfer_error(self, user_id: int, log_description: str, reason: str) -> None:
        """Сообщает об ошибке передачи данных на сайт, используя следующие способы:
        - в лог;
        - на почту админу;
        - техническое сообщение админу.
        """
        message = f"Ошибка передачи данных на сайт: {log_description} пользователя {user_id}. {reason}"
        await logger.ainfo(message)
        await self._tech_message_service.create(message)
        if self._settings.EMAIL_TO_ADMIN_OF_DATA_TRANSFER_ERROR:
            await self._email_provider.notify_admin_of_data_transfer_error(message, self._settings.EMAIL_ADMIN)

    async def send_user_categories(self, user_id: int, user_categories: list[int]) -> bool:
        """Отправляет запрос на сайт с обновленными категориями пользователя.

        Args:
            user_id: идентификатор пользователя на сайте.
            user_categories: список идентификаторов выбранных категорий.
        Return:
            True: отправка выполнена успешно;
            False: отправка выполнена неуспешно.
        """
        specializations = ", ".join(map(str, user_categories))
        body_schema = SiteUserCategoriesRequest(user_id=user_id, specializations=specializations)
        return await self._site_post(
            url=self._settings.procharity_send_user_categories_api_url,
            data=body_schema.model_dump_json(),
            user_id=user_id,
            log_description="категории",
        )

    async def send_user_bot_status(self, user: User) -> bool | None:
        """Отправляет запрос на сайт с обновленным статусом бота пользователя.

        Args:
            user: Модель пользователя.
        Return:
            True: отправка выполнена успешно;
            False: отправка выполнена неуспешно;
            None: отправка не выполнялась.
        """
        if user and user.external_user:
            user_id = user.external_user.external_id
            status = "off" if user.banned or (user.is_volunteer and not user.has_mailing) else "on"
            if user.is_volunteer:
                site_url = self._settings.procharity_send_bot_status_volunteer_api_url
                body_schema = SiteBotStatusVolunteerRequest(
                    user_id=user_id,
                    bot_status=status,
                    bot_blocked=user.banned,
                    has_mailing_new_tasks=user.has_mailing,
                    has_mailing_profile=user.external_user.has_mailing_profile,
                    has_mailing_my_tasks=user.external_user.has_mailing_my_tasks,
                    has_mailing_procharity=user.external_user.has_mailing_procharity,
                )
            else:
                site_url = self._settings.procharity_send_bot_status_fund_api_url
                body_schema = SiteBotStatusFundRequest(
                    user_id=user_id,
                    bot_status=status,
                    bot_blocked=user.banned,
                    has_mailing_profile=user.external_user.has_mailing_profile,
                    has_mailing_my_tasks=user.external_user.has_mailing_my_tasks,
                    has_mailing_procharity=user.external_user.has_mailing_procharity,
                )

            return await self._site_post(
                url=site_url,
                data=body_schema.model_dump_json(exclude_none=True),
                user_id=user_id,
                log_description="статус бота",
            )

    async def send_task_respond_status(
        self,
        user_id: int,
        task_id: int,
        status: UserResponseAction,
        cancel_reason: CANCEL_RESPOND_REASONS | None = None,
    ):
        """Отправляет запрос на сайт с обновленным откликом пользователя на задачу.

        Args:
            user_id: Идентификатор пользователя.
            task_id: Идентификатор задачи.
            status: Статус отклика на задачу.
            cancel_reason: Причина отмены отклика.
        """
        body_schema = SiteBotRespondRequest(
            user_id=user_id, task_id=task_id, status=status, cancel_reason=cancel_reason
        )
        await self._site_post(
            url=self._settings.procharity_send_bot_respond_api_url,
            data=body_schema.model_dump_json(exclude_none=True),
            user_id=user_id,
            log_description="статус отклика",
        )
