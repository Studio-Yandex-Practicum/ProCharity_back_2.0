from dependency_injector.wiring import Provide
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.constants import callback_data, enum
from src.bot.web_apps import get_feedback_web_app_info, get_task_web_app_info
from src.core.db.models import Category, Task, User
from src.core.depends import Container
from src.core.enums import UserRoles
from src.settings import settings

VIEW_TASKS_BUTTON = [InlineKeyboardButton("🔎 Посмотреть актуальные задания", callback_data=callback_data.VIEW_TASKS)]
VIEW_CURRENT_TASKS_BUTTON = [
    InlineKeyboardButton("Посмотреть актуальные задания", callback_data=callback_data.VIEW_TASKS)
]
VIEW_CATEGORIES_BUTTON = [InlineKeyboardButton("🎓 Изменить компетенции", callback_data=callback_data.VIEW_CATEGORIES)]
CHANGE_CATEGORY_BUTTON = [InlineKeyboardButton("✍ Изменить", callback_data=callback_data.CHANGE_CATEGORY)]
ALL_RIGHT_CATEGORY_BUTTON = [InlineKeyboardButton("👌 Всё верно", callback_data=callback_data.MENU)]
UNSUBSCRIBE_BUTTON = [InlineKeyboardButton("⏸ Отписаться от заданий", callback_data=callback_data.JOB_SUBSCRIPTION)]
SUBSCRIBE_BUTTON = [InlineKeyboardButton("▶️ Подписаться на задания", callback_data=callback_data.JOB_SUBSCRIPTION)]
OPEN_MENU_BUTTON = [InlineKeyboardButton("Открыть меню", callback_data=callback_data.MENU)]
RETURN_MENU_BUTTON = [InlineKeyboardButton("Вернуться в меню", callback_data=callback_data.MENU)]
CHECK_CATEGORIES_BUTTON = [
    InlineKeyboardButton("Перепроверить компетенции", callback_data=callback_data.CONFIRM_CATEGORIES)
]
SHOW_MORE_TASKS_BUTTON = [InlineKeyboardButton("Показать ещё задания", callback_data=callback_data.VIEW_TASKS)]
SUPPORT_SERVICE_BUTTON = [
    InlineKeyboardButton("✍ Написать в службу поддержки", callback_data=callback_data.SUPPORT_SERVICE)
]


def get_personal_account_button(
    registration_url: str = Provide[Container.settings.provided.procharity_registration_url],
) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton("🚪 Войти в личный кабинет", url=registration_url)]


def get_notification_settings_button(
    volunteer_auth_url: str = Provide[Container.settings.provided.procharity_volunteer_auth_url],
) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton("🚪 Изменить настройку уведомлений", url=volunteer_auth_url)]


def get_support_service_button(user: User) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton("✍ Написать в службу поддержки", web_app=get_feedback_web_app_info(user))]


async def get_checked_categories_keyboard(
    categories: list[str, int, int], selected_categories: dict[Category] = None
) -> InlineKeyboardMarkup:
    keyboard = []
    selected_categories = {} if selected_categories is None else selected_categories
    for category_name, category_id, category_children_count in categories:
        if category_id in selected_categories:
            if category_children_count == len(selected_categories[category_id]):
                button = InlineKeyboardButton(f"✅ {category_name}", callback_data=f"category_{category_id}")
            else:
                button = InlineKeyboardButton(f"☑️  {category_name}", callback_data=f"category_{category_id}")
        else:
            button = InlineKeyboardButton(category_name, callback_data=f"category_{category_id}")
        keyboard.append([button])

    keyboard.append(
        [InlineKeyboardButton("Готово 👌", callback_data=callback_data.CONFIRM_CATEGORIES)],
    )
    return InlineKeyboardMarkup(keyboard)


async def get_view_categories_keyboard() -> InlineKeyboardMarkup:
    keyboard = [ALL_RIGHT_CATEGORY_BUTTON, CHANGE_CATEGORY_BUTTON]
    return InlineKeyboardMarkup(keyboard)


async def get_subcategories_keyboard(
    parent_id: int,
    subcategories: list[Category],
    selected_categories: dict[Category] = None,
) -> InlineKeyboardMarkup:
    keyboard = []
    selected_categories = {} if selected_categories is None else selected_categories
    for category in subcategories:
        if category.id not in selected_categories:
            button = InlineKeyboardButton(category.name, callback_data=f"select_category_{category.id}")
        else:
            button = InlineKeyboardButton(f"✅ {category.name}", callback_data=f"select_category_{category.id}")
        keyboard.append([button])

    keyboard.append([InlineKeyboardButton("Назад ⬅️", callback_data=f"back_to_{parent_id}")])
    return InlineKeyboardMarkup(keyboard)


async def support_service_keyboard(user: User) -> InlineKeyboardMarkup:
    keyboard = [
        get_support_service_button(user),
        [InlineKeyboardButton(text="Вернуться в меню", callback_data=callback_data.MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    keyboard = [
        VIEW_TASKS_BUTTON,
        SUPPORT_SERVICE_BUTTON,
        UNSUBSCRIBE_BUTTON if user.has_mailing else SUBSCRIBE_BUTTON,
        VIEW_CATEGORIES_BUTTON,
        get_notification_settings_button(),
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_unregistered_user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([get_personal_account_button()])


async def get_back_menu() -> InlineKeyboardMarkup:
    keyboard = [
        RETURN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_start_keyboard(user_role: str) -> InlineKeyboardMarkup:
    keyboard = [
        CHECK_CATEGORIES_BUTTON if user_role == UserRoles.VOLUNTEER else [],
        OPEN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_tasks_and_open_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        VIEW_CURRENT_TASKS_BUTTON,
        OPEN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def view_more_tasks_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        SHOW_MORE_TASKS_BUTTON,
        OPEN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_tasks_and_back_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        VIEW_TASKS_BUTTON,
        RETURN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


def get_no_mailing_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с причинами отписки от рассылки на почту"""
    keyboard = [[InlineKeyboardButton(reason, callback_data=f"reason_{reason.name}")] for reason in enum.REASONS]
    keyboard.append([InlineKeyboardButton("↩️ Не отменять подписку", callback_data=callback_data.MENU)])
    return InlineKeyboardMarkup(keyboard)


def get_task_info_keyboard(task: Task) -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой для отображения подробной информации о задании и фонде"""
    keyboard = [[InlineKeyboardButton("ℹ️ Посмотреть задание", web_app=get_task_web_app_info(task))]]
    return InlineKeyboardMarkup(keyboard)
