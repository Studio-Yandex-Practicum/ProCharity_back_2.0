from urllib.parse import urljoin

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from src.api.schemas import FeedbackFormQueryParams
from src.bot.constants import callback_data, enum
from src.core.db.models import Category, User
from src.settings import settings

VIEW_TASKS_BUTTON = [InlineKeyboardButton("🔎 Посмотреть актуальные задания", callback_data=callback_data.VIEW_TASKS)]
CHANGE_CATEGORY_BUTTON = [InlineKeyboardButton("🎓 Изменить компетенции", callback_data=callback_data.CHANGE_CATEGORY)]
ABOUT_PROJECT_BUTTON = [InlineKeyboardButton("ℹ️ О платформе", callback_data=callback_data.ABOUT_PROJECT)]
UNSUBSCRIBE_BUTTON = [
    InlineKeyboardButton("⏹️ Отменить подписку на задания", callback_data=callback_data.JOB_SUBSCRIPTION)
]
SUBSCRIBE_BUTTON = [InlineKeyboardButton("▶️ Подписаться на задания", callback_data=callback_data.JOB_SUBSCRIPTION)]
PERSONAL_ACCOUNT_BUTTON = [
    InlineKeyboardButton("🚪 Изменить настройку уведомлений", url="https://procharity.ru/volunteers/settings/")
]
OPEN_MENU_BUTTON = [InlineKeyboardButton(text="Открыть меню", callback_data=callback_data.MENU)]
RETURN_MENU_BUTTON = [InlineKeyboardButton(text="Вернуться в меню", callback_data=callback_data.MENU)]


def get_support_service_button(user: User) -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton("✍ Написать в службу поддержки", web_app=get_feedback_web_app_info(user))]


async def get_checked_categories_keyboard(
    categories: dict[str, int, int], selected_categories: dict[Category] = {}
) -> InlineKeyboardButton:
    keyboard = []

    for category_name, category_id, category_children_count in categories:
        if category_id in selected_categories:
            if category_children_count == len(selected_categories[category_id]):
                button = InlineKeyboardButton(f"✅ {category_name}", callback_data=f"category_{category_id}")
            else:
                button = InlineKeyboardButton(f"☑️  {category_name}", callback_data=f"category_{category_id}")
        else:
            button = InlineKeyboardButton(category_name, callback_data=f"category_{category_id}")
        keyboard.append([button])

    keyboard.extend(
        [
            [InlineKeyboardButton("Нет моих компетенций 😕", callback_data=callback_data.ADD_CATEGORIES)],
            [InlineKeyboardButton("Готово 👌", callback_data=callback_data.CONFIRM_CATEGORIES)],
        ]
    )
    return InlineKeyboardMarkup(keyboard)


async def get_subcategories_keyboard(
    parent_id: int, subcategories: list[Category], selected_categories: dict[Category] = {}
) -> InlineKeyboardMarkup:
    keyboard = []

    for category in subcategories:
        if category.id not in selected_categories:
            button = InlineKeyboardButton(category.name, callback_data=f"select_category_{category.id}")
        else:
            button = InlineKeyboardButton(f"✅ {category.name}", callback_data=f"select_category_{category.id}")
        keyboard.append([button])

    keyboard.append([InlineKeyboardButton("Назад ⬅️", callback_data=f"back_to_{parent_id}")])
    return InlineKeyboardMarkup(keyboard)


async def get_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    keyboard = [
        VIEW_TASKS_BUTTON,
        get_support_service_button(user),
        UNSUBSCRIBE_BUTTON if user.has_mailing else SUBSCRIBE_BUTTON,
        CHANGE_CATEGORY_BUTTON,
        PERSONAL_ACCOUNT_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


def get_feedback_web_app_info(user: User) -> WebAppInfo:
    return WebAppInfo(
        url=urljoin(
            settings.feedback_form_template_url,
            FeedbackFormQueryParams(
                external_id=user.external_user.external_id if user.external_user else None,
                telegram_link=user.telegram_link,
                name=user.first_name,
                surname=user.last_name,
                email=getattr(user, "email", None),
            ).as_url_query(),
        )
    )


async def get_back_menu() -> InlineKeyboardMarkup:
    keyboard = [
        RETURN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Перепроверить компетенции", callback_data=callback_data.CONFIRM_CATEGORIES)],
        OPEN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_tasks_and_open_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Посмотреть актуальные задания", callback_data=callback_data.VIEW_TASKS)],
        OPEN_MENU_BUTTON,
    ]
    return InlineKeyboardMarkup(keyboard)


async def view_more_tasks_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Показать ещё задания", callback_data=callback_data.VIEW_TASKS)],
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
    return InlineKeyboardMarkup(keyboard)
