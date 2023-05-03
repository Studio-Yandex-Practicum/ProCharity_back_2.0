from telegram import InlineKeyboardButton

from constaints.callback_data import (VIEW_TASKS, CHANGE_CATEGORY,
                                      SEND_ERROR_OR_PROPOSAL,
                                      ASK_YOUR_QUESTION, ABOUT_PROJECT,
                                      JOB_SUBSCRIPTION)


KEYBOARD = [
    [InlineKeyboardButton(
        "Посмотреть открытые задания",
        callback_data=VIEW_TASKS
    )],
    [InlineKeyboardButton(
        "Изменить компетенции",
        callback_data=CHANGE_CATEGORY
    )],
    [InlineKeyboardButton(
        "Отправить предложение/ошибку",
        callback_data=SEND_ERROR_OR_PROPOSAL
    )],
    [InlineKeyboardButton(
        "Задать свой вопрос",
        callback_data=ASK_YOUR_QUESTION
    )],
    [InlineKeyboardButton(
        "О платформе",
        callback_data=ABOUT_PROJECT
    )],
    [InlineKeyboardButton(
        "⏹️ Остановить / ▶️ включить подписку на задания",
        callback_data=JOB_SUBSCRIPTION
    )],
]
