from dependency_injector.wiring import Provide
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CallbackQueryHandler

from src.bot.constants import callback_data, patterns
from src.bot.keyboards import get_back_menu, view_more_tasks_keyboard
from src.bot.services.task import TaskService
from src.bot.utils import delete_previous_message
from src.core.logging.utils import logger_decor
from src.core.utils import display_task_verbosely, display_tasks
from src.depends import Container


@logger_decor
async def task_details_callback(
    update: Update,
    context: CallbackContext,
    task_service: TaskService = Provide[Container.bot_task_service],
):
    query = update.callback_query
    task_service = task_service
    task_id = int(context.match.group(1))
    task = await task_service.get_task_by_id(task_id)
    detailed_text = display_task_verbosely(task)
    await query.message.edit_text(detailed_text)


@logger_decor
@delete_previous_message
async def view_task_callback(
    update: Update,
    context: CallbackContext,
    limit: int = 3,
    task_service: TaskService = Provide[Container.bot_task_service],
):
    task_service = task_service
    telegram_id = context._user_id
    tasks_to_show, offset, page_number = await task_service.get_user_tasks_by_page(
        context.user_data.get("page_number", 1),
        limit,
        telegram_id,
    )

    for task in tasks_to_show:
        message = display_tasks(task)
        inline_keyboard = [[InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"task_details_{task.id}")]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=reply_markup,
        )
    remaining_tasks = await task_service.get_remaining_user_tasks_count(limit, offset, telegram_id)
    await show_next_tasks(update, context, page_number, remaining_tasks)


@delete_previous_message
async def show_next_tasks(update: Update, context: CallbackContext, page_number: int, remaining_tasks: int):
    if remaining_tasks > 0:
        text = f"Есть ещё задания, показать? Осталось: {remaining_tasks}"
        context.user_data["page_number"] = page_number + 1
        keyboard = await view_more_tasks_keyboard()
    else:
        text = "Заданий больше нет."
        keyboard = await get_back_menu()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard,
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(view_task_callback, pattern=callback_data.VIEW_TASKS))
    app.add_handler(CallbackQueryHandler(task_details_callback, pattern=patterns.TASK_DETAILS))
