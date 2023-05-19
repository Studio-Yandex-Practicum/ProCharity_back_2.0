from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.services.category import CategoryService
from src.bot.constants import callback_data


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


async def get_categories_keyboard():
    category_service = CategoryService()
    categories = await category_service.get_unarchived_parents()
    keyboard = [
        [InlineKeyboardButton(category.name, callback_data=f"category_{category.id}")] for category in categories
    ]
    keyboard.extend(
        [
            [InlineKeyboardButton("Нет моих компетенций 😕", callback_data="add_categories")],
            [InlineKeyboardButton("Готово 👌", callback_data="confirm_categories")],
        ]
    )

    return InlineKeyboardMarkup(keyboard)


async def get_subcategories_keyboard(parent_id, context):
    category_service = CategoryService()
    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    keyboard = [
        [InlineKeyboardButton(category.name, callback_data=f"select_category_{category.id}")]
        if category.id not in context.user_data.get("selected_categories", [])
        else [InlineKeyboardButton(f"✅ {category.name}", callback_data=f"select_category_{category.id}")]
        for category in subcategories
    ]

    keyboard.append([InlineKeyboardButton("Назад ⬅️", callback_data=f"back_to_{parent_id}")])
    return InlineKeyboardMarkup(keyboard)
