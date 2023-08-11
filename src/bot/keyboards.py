from urllib.parse import urljoin

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from src.api.schemas import FeedbackFormQueryParams
from src.bot.constants import callback_data, enum, urls
from src.core.db.models import Category, User
from src.settings import settings

MENU_KEYBOARD = [
    [InlineKeyboardButton("🔎 Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    [InlineKeyboardButton("✏️ Изменить компетенции", callback_data=callback_data.CHANGE_CATEGORY)],
    [InlineKeyboardButton("ℹ️ О платформе", callback_data=callback_data.ABOUT_PROJECT)],
]
UNSUBSCRIBE_BUTTON = [
    InlineKeyboardButton("⏹️ Остановить подписку на задания", callback_data=callback_data.JOB_SUBSCRIPTION)
]
SUBSCRIBE_BUTTON = [
    InlineKeyboardButton("▶️ Включить подписку на задания", callback_data=callback_data.JOB_SUBSCRIPTION)
]
SUGGESTION_BUTTON_TITLE = "✉️ Отправить предложение/ошибку"
QUESTION_BUTTON_TITLE = "❓ Задать вопрос"


async def get_categories_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(category.name, callback_data=f"category_{category.id}")] for category in categories
    ]
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
    keyboard = []
    keyboard.extend(MENU_KEYBOARD)
    # Кнопка включения/выключения подписки на новые заказы
    if user.has_mailing:
        keyboard.extend([UNSUBSCRIBE_BUTTON])
    else:
        keyboard.extend([SUBSCRIBE_BUTTON])
    # Кнопки обратной связи
    web_app = WebAppInfo(
        url=urljoin(
            settings.feedback_form_template_url,
            FeedbackFormQueryParams(name=user.first_name, surname=user.last_name, email=user.email).as_url_query(),
        )
    )
    keyboard.extend(
        [
            [InlineKeyboardButton(QUESTION_BUTTON_TITLE, web_app=web_app)],
            [InlineKeyboardButton(SUGGESTION_BUTTON_TITLE, web_app=web_app)],
        ]
    )
    return InlineKeyboardMarkup(keyboard)


async def get_back_menu() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="Вернуться в меню", callback_data=callback_data.MENU)]]
    return InlineKeyboardMarkup(keyboard)


async def get_start_keyboard(callback_data_on_start: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Начнём", callback_data=callback_data_on_start)],
        [InlineKeyboardButton("Перейти на сайт ProCharity", url=urls.PROCHARITY_URL)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_open_tasks_and_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Посмотреть открытые задачи", callback_data=callback_data.VIEW_TASKS)],
        [InlineKeyboardButton("Открыть меню", callback_data=callback_data.MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


async def view_more_tasks_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="Показать ещё задания", callback_data=callback_data.VIEW_TASKS)],
        [InlineKeyboardButton(text="Открыть меню", callback_data=callback_data.MENU)],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Да", callback_data=callback_data.CONFIRM_CATEGORIES)],
        [InlineKeyboardButton("Нет, хочу изменить", callback_data=callback_data.CHANGE_CATEGORY)],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_no_mailing_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с причинами отписки от рассылки на почту"""
    keyboard = [[InlineKeyboardButton(reason, callback_data=f"reason_{reason.name}")] for reason in enum.REASONS]
    return InlineKeyboardMarkup(keyboard)
