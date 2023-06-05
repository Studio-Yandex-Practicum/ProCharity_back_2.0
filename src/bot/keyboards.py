from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.constants import callback_data
from src.core.services.user import UserService
from src.bot.services.category import CategoryService

MENU_KEYBOARD = [
    [InlineKeyboardButton("Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    [InlineKeyboardButton("Изменить компетенции", callback_data=callback_data.CHANGE_CATEGORY)],
    [InlineKeyboardButton("Отправить предложение/ошибку", callback_data=callback_data.SEND_ERROR_OR_PROPOSAL)],
    [InlineKeyboardButton("Задать свой вопрос", callback_data=callback_data.ASK_YOUR_QUESTION)],
    [InlineKeyboardButton("О платформе", callback_data=callback_data.ABOUT_PROJECT)],
]
UNSUBSCRIBE_BUTTON = [
    InlineKeyboardButton(
        "⏹️ Остановить подписку на задания", callback_data=callback_data.JOB_SUBSCRIPTION
    )
]
SUBSCRIBE_BUTTON = [
    InlineKeyboardButton(
        "▶️ Включить подписку на задания", callback_data=callback_data.JOB_SUBSCRIPTION
    )
]


async def get_categories_keyboard() -> InlineKeyboardMarkup:
    category_service = CategoryService()
    categories = await category_service.get_unarchived_parents()
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


async def get_subcategories_keyboard(parent_id: int, context: CallbackContext) -> InlineKeyboardMarkup:
    category_service = CategoryService()
    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    keyboard = []
    selected_categories = context.user_data.get("selected_categories", {})

    for category in subcategories:
        if category.id not in selected_categories:
            button = InlineKeyboardButton(category.name, callback_data=f"select_category_{category.id}")
        else:
            button = InlineKeyboardButton(f"✅ {category.name}", callback_data=f"select_category_{category.id}")
        keyboard.append([button])

    keyboard.append([InlineKeyboardButton("Назад ⬅️", callback_data=f"back_to_{parent_id}")])
    return InlineKeyboardMarkup(keyboard)


async def get_menu_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    keyboard = []
    keyboard.extend(MENU_KEYBOARD)
    user_service = UserService()
    has_mailing = await user_service.get_tasks_mailing(telegram_id=telegram_id)
    if has_mailing:
        keyboard.extend([UNSUBSCRIBE_BUTTON])
    else:
        keyboard.extend([SUBSCRIBE_BUTTON])
    return InlineKeyboardMarkup(keyboard)
