from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.constants import callback_data
from src.core.db.models import Category

MENU_KEYBOARD = [
    [InlineKeyboardButton("Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    [InlineKeyboardButton("Изменить компетенции", callback_data=callback_data.CHANGE_CATEGORY)],
    [InlineKeyboardButton("Отправить предложение/ошибку", callback_data=callback_data.SEND_ERROR_OR_PROPOSAL)],
    [InlineKeyboardButton("Задать свой вопрос", callback_data=callback_data.ASK_YOUR_QUESTION)],
    [InlineKeyboardButton("О платформе", callback_data=callback_data.ABOUT_PROJECT)],
    [
        InlineKeyboardButton(
            "⏹️ Остановить / ▶️ включить подписку на задания", callback_data=callback_data.JOB_SUBSCRIPTION
        )
    ],
]


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
    parent_id: int, subcategories: list[Category], context: CallbackContext
) -> InlineKeyboardMarkup:
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
