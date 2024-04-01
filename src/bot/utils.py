from functools import wraps
from typing import Iterable, ParamSpec, Protocol, TypeVar

from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.bot.keyboards import get_unregistered_user_keyboard
from src.bot.services import ExternalSiteUserService
from src.core.depends import Container

ReturnType = TypeVar("ReturnType")
ParameterTypes = ParamSpec("ParameterTypes")


class FuncT(Protocol[ParameterTypes, ReturnType]):
    async def __call__(self, update: Update, *args: ParameterTypes.args, **kw: ParameterTypes.kwargs) -> ReturnType:
        pass


def delete_previous_message(coroutine: FuncT[ParameterTypes, ReturnType]) -> FuncT[ParameterTypes, ReturnType]:
    """Декоратор для функций, отправляющих новые сообщения с inline-кнопками.
    После выполнения оборачиваемой функции удаляет сообщение с inline-кнопкой,
    нажатие на которую повлекло вызов оборачиваемой функции."""

    @wraps(coroutine)
    async def wrapper(update: Update, *args: ParameterTypes.args, **kwargs: ParameterTypes.kwargs) -> ReturnType:
        result = await coroutine(update, *args, **kwargs)
        if update.callback_query is not None and update.callback_query.message is not None:
            await update.callback_query.message.delete()
        return result

    return wrapper


def registered_user_required(handler: FuncT[ParameterTypes, ReturnType]) -> FuncT[ParameterTypes, ReturnType]:
    """Декоратор для обработчиков событий, проверяющий что текущий пользователь авторизован.

    Если пользователь авторизован (т.е. для него имеется запись в таблице external_site_users),
    то вызывается обработчик (он получает дополнительный аргумент ext_site_user: ExternalSiteUser),
    в противном случае выводится сообщение о необходимости регистрации и обработчик не вызывается.
    Если обработчик вызван с аргументом (id_hash), то запись в таблице external_site_users ищется по нему,
    в противном случает она ищется по telegram_id.
    """

    @wraps(handler)
    @inject
    async def decorated_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        ext_site_user_service: ExternalSiteUserService = Provide[
            Container.bot_services_container.bot_site_user_service
        ],
        *args,
        **kwargs,
    ):
        telegram_user = update.effective_user
        id_hash = context.args[0] if context.args and len(context.args) == 1 else None
        ext_site_user = (
            await ext_site_user_service.get_by_id_hash(id_hash)
            if id_hash
            else await ext_site_user_service.get_by_telegram_id(telegram_user.id)
        )
        if ext_site_user:
            await handler(update, context, ext_site_user, *args, **kwargs)
        else:
            keyboard = await get_unregistered_user_keyboard()
            await context.bot.send_message(
                chat_id=telegram_user.id,
                text=(
                    "<b>Добро пожаловать на ProCharity!</b>\n\n"
                    "Чтобы получить доступ к боту, "
                    "авторизуйтесь или зарегистрируйтесь на платформе."
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )

    return decorated_handler


def get_connection_url(
    telegram_id: int,
    external_id: int | None = None,
    procharity_url: str = Provide[Container.settings.provided.PROCHARITY_URL],
) -> str:
    """Получение ссылки для связи аккаунта с ботом по external_id и telegram_id.
    В случае отсутствия external_id возвращает ссылку на страницу авторизации"""
    if external_id:
        return f"{procharity_url}auth/bot_procharity.php?user_id={external_id}&telegram_id={telegram_id}"
    return f"{procharity_url}auth/"


def get_marked_list(items: Iterable[str], marker: str) -> str:
    """Получение маркированного списка элементов items с маркером marker."""
    return "\n".join(marker + item for item in items)
