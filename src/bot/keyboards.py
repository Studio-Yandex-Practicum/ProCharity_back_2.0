from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from src.bot.services.category import CategoryService
from src.bot.constants import callback_data, keyboards_const


MENU_KEYBOARD = [
    [
        InlineKeyboardButton(
            keyboards_const.VIEW_OPEN_TASKS_TEXT,
            callback_data=callback_data.VIEW_TASKS
        )
    ],
    [
        InlineKeyboardButton(
            keyboards_const.EDIT_COMPETENTIONS_TEXT,
            callback_data=callback_data.CHANGE_CATEGORY
        )
    ],
    [
        InlineKeyboardButton(
            keyboards_const.SEND_OFFER_TEXT,
            callback_data=callback_data.SEND_ERROR_OR_PROPOSAL
        )
    ],
    [
        InlineKeyboardButton(
            keyboards_const.ASK_QUESTION_TEXT,
            callback_data=callback_data.ASK_YOUR_QUESTION
        )
    ],
    [
        InlineKeyboardButton(
            keyboards_const.ABOUT_TEXT,
            callback_data=callback_data.ABOUT_PROJECT
        )
    ],
    [
        InlineKeyboardButton(
            keyboards_const.STOP_RUN_SUBSCRIPTION_TEXT,
            callback_data=callback_data.JOB_SUBSCRIPTION
        )
    ],
]


async def get_categories_keyboard() -> InlineKeyboardMarkup:
    category_service = CategoryService()
    categories = await category_service.get_unarchived_parents()
    keyboard = [
        [InlineKeyboardButton(category.name, callback_data=f"category_{category.id}")] for category in categories
    ]
    keyboard.extend(
        [
            [
                InlineKeyboardButton(
                    keyboards_const.NO_COMPETENTIONS_TEXT,
                    callback_data=callback_data.ADD_CATEGORIES
                )
            ],
            [
                InlineKeyboardButton(
                    keyboards_const.DONE_TEXT,
                    callback_data=callback_data.CONFIRM_CATEGORIES)],
        ]
    )

    return InlineKeyboardMarkup(keyboard)


async def get_subcategories_keyboard(parent_id: int, context: CallbackContext) -> InlineKeyboardMarkup:
    category_service = CategoryService()
    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    keyboard = []
    selected_categories = context.user_data.get(callback_data.SELECTED_CATEGORIES, {})

    for category in subcategories:
        if category.id not in selected_categories:
            button = InlineKeyboardButton(category.name, callback_data=f"select_category_{category.id}")
        else:
            button = InlineKeyboardButton(f"✅ {category.name}", callback_data=f"select_category_{category.id}")
        keyboard.append([button])

    keyboard.append([InlineKeyboardButton(keyboards_const.BACK_TEXT, callback_data=f"back_to_{parent_id}")])
    return InlineKeyboardMarkup(keyboard)
