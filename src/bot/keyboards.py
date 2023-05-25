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

# Галочки по началу ставятся, но не сохраняются. потом выходит ошибка 
# BadRequest: Message is not modified: specified new message content 
# and reply markup are exactly the same as a current content and reply
# markup of the message.
# это видимо из-за кортежа..
## Если передавать только parent_id, selected_categories (бе звездочек), то ошибка 
# про то, что CallBack не итерируетсяTypeError: argument of type 'CallbackContext' is not iterable

async def get_subcategories_keyboard(parent_id, *selected_categories):
    category_service = CategoryService()

    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    keyboard = []

    selected_categories = selected_categories

    for category in subcategories:
        if category.id not in selected_categories:
            button = InlineKeyboardButton(category.name, callback_data=f"select_category_{category.id}")
        else:
            button = InlineKeyboardButton(f"✅ {category.name}", callback_data=f"select_category_{category.id}")
        keyboard.append([button])

    keyboard.append([InlineKeyboardButton("Назад ⬅️", callback_data=f"back_to_{parent_id}")])
    return InlineKeyboardMarkup(keyboard)