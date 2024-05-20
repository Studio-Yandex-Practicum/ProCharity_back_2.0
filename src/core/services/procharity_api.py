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

    async def _site_post(self, url: str, data: str, user_id: str, log_description: str):
        """Осуществляет post запрос на заданный url сайта.

        Args:
            url: Адрес запроса.
            data: Данные запроса.
            user_id: Идентификатор пользователя (для логирования).
            log_description: Описание запроса (для логирования).
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=data, headers=self.token_header_dict) as response:
                    if response.status != 200:
                        await logger.ainfo(
                            (
                                f"Ошибка передачи данных из бота: {log_description} пользователя {user_id}. "
                                f"status = {response.status}"
                            )
                        )
                    else:
                        data = await response.json()
                        await logger.adebug(
                            f"Успешная передача данных из бота: {log_description} пользователя {user_id}. Ответ: {data}"
                        )
        except Exception as e:
            await logger.aexception(e)

    async def send_user_categories(self, user_id: int, user_categories: list[int]):
        """Отправляет запрос на сайт с обновленными категориями пользователя.

        Args:
            user_id: идентификатор пользователя на сайте.
            user_categories: список идентификаторов выбранных категорий.
        """
        specializations = ", ".join(map(str, user_categories))
        body_schema = SiteUserCategoriesRequest(user_id=user_id, specializations=specializations)
        await self._site_post(
            url=self._settings.procharity_send_user_categories_api_url,
            data=body_schema.model_dump_json(),
            user_id=user_id,
            log_description="категории",
        )

    async def send_user_bot_status(self, user: User):
        """Отправляет запрос на сайт с обновленным статусом бота пользователя.

        Args:
            user: Модель пользователя.
        """
        if user and user.external_user:
            user_id = user.external_user.external_id
            status = "off" if user.banned or (user.is_volunteer and not user.has_mailing) else "on"
            site_url = (
                self._settings.procharity_send_bot_status_volunteer_api_url
                if user.is_volunteer
                else self._settings.procharity_send_bot_status_fund_api_url
            )
            body_schema = SiteBotStatusRequest(user_id=user_id, bot_status=status)
            await self._site_post(
                url=site_url,
                data=body_schema.model_dump_json(),
                user_id=user_id,
                log_description="статус бота",
            )
