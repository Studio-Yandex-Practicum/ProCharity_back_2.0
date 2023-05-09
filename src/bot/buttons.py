from telegram import InlineKeyboardButton

from src.bot.constants import callback_data


MENU_KEYBOARD = [
    [InlineKeyboardButton(
        "Посмотреть открытые задания",
        callback_data=callback_data.VIEW_TASKS
    )],
    [InlineKeyboardButton(
        "Изменить компетенции",
        callback_data=callback_data.CHANGE_CATEGORY
    )],
    [InlineKeyboardButton(
        "Отправить предложение/ошибку",
        callback_data=callback_data.SEND_ERROR_OR_PROPOSAL
    )],
    [InlineKeyboardButton(
        "Задать свой вопрос",
        callback_data=callback_data.ASK_YOUR_QUESTION
    )],
    [InlineKeyboardButton(
        "О платформе",
        callback_data=callback_data.ABOUT_PROJECT
    )],
    [InlineKeyboardButton(
        "⏹️ Остановить / ▶️ включить подписку на задания",
        callback_data=callback_data.JOB_SUBSCRIPTION
    )],
]
