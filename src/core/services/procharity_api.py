import aiohttp
from structlog import get_logger

from src.core.db.models import User
from src.core.schemas.procharity_api import SiteBotStatusRequest, SiteUserCategoriesRequest
from src.settings import Settings

logger = get_logger(module=__name__)


class ProcharityAPI:
    """Класс для отправки сообщений на API сайта."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def token_header_dict(self) -> dict[str, str]:
        """Возвращает заголовок с токеном авторизации в виде словаря."""
        return {"token": self._settings.ACCESS_TOKEN_SEND_DATA_TO_PROCHARITY}

    async def send_user_categories(self, user_id: int, user_categories: list[int]):
        """Отправляет запрос на сайт с обновленными категориями пользователя.

        Args:
            user_id: идентификатор пользователя на сайте.
            user_categories: список идентификаторов выбранных категорий.
        """
        specializations = ", ".join(map(str, user_categories))
        body_schema = SiteUserCategoriesRequest(user_id=user_id, specializations=specializations)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self._settings.procharity_send_user_categories_api_url,
                    data=body_schema.model_dump_json(),
                    headers=self.token_header_dict,
                ) as response:
                    if response.status != 200:
                        await logger.ainfo(
                            f"Ошибка обновления категорий пользователя {user_id}: status = {response.status}"
                        )
                    else:
                        data = await response.json()
                        await logger.adebug(f"Отправлены обновленные категории пользователя {user_id}. Ответ: {data}")
        except Exception as e:
            await logger.aexception(e)

    async def send_bot_status(self, user_id: int, is_volunteer: bool, has_mailing: bool, banned: bool):
        """Отправляет запрос на сайт с обновленным статусом бота пользователя.

        Args:
            user_id: Идентификатор пользователя на сайте.
            is_volunteer: True для волонтера, False для фонда.
            has_mailing: True, если рассылка включена.
            banned: True, если пользователь забанил бота.
        """
        status = "on" if has_mailing and not banned else "off"
        site_url = (
            self._settings.procharity_send_bot_status_volunteer_api_url
            if is_volunteer
            else self._settings.procharity_send_bot_status_fund_api_url
        )
        body_schema = SiteBotStatusRequest(user_id=user_id, bot_status=status)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=site_url,
                    data=body_schema.model_dump_json(),
                    headers=self.token_header_dict,
                ) as response:
                    if response.status != 200:
                        await logger.ainfo(
                            f"Ошибка обновления статуса бота пользователя {user_id}: status = {response.status}"
                        )
                    else:
                        data = await response.json()
                        await logger.adebug(f"Отправлен обновленный статус бота пользователя {user_id}. Ответ: {data}")
        except Exception as e:
            await logger.aexception(e)

    async def send_user_bot_status(self, user: User):
        """Отправляет запрос на сайт с обновленным статусом бота пользователя.

        Args:
            user: Модель пользователя.
        """
        if user and user.external_user:
            await self.send_bot_status(
                user_id=user.external_user.external_id,
                is_volunteer=user.is_volunteer,
                has_mailing=user.has_mailing,
                banned=user.banned,
            )
