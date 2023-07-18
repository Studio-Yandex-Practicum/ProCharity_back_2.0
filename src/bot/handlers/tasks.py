from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CallbackQueryHandler

from src.bot.constants import callback_data, patterns
from src.bot.handlers.categories import back_subcategory_callback, select_subcategory_callback, subcategories_callback
from src.bot.keyboards import get_back_menu, view_more_tasks_keyboard
from src.bot.services.task import TaskService
from src.bot.utils import delete_previous_message
from src.core.logging.utils import logger_decor
from src.core.utils import display_tasks


@logger_decor
@delete_previous_message
async def view_task_callback(update: Update, context: CallbackContext, limit: int = 3):
    task_service = TaskService()
    tasks_to_show, offset, page_number = await task_service.get_user_tasks_by_page(
        context.user_data.get("page_number", 1), limit
    )

    for task in tasks_to_show:
        message = display_tasks(task)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    await show_next_tasks(update, context, limit, offset, page_number)


@delete_previous_message
async def show_next_tasks(update: Update, context: CallbackContext, limit: int, offset: int, page_number: int):
    task_service = TaskService()
    remaining_tasks = await task_service.get_remaining_user_tasks_count(limit, offset)

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
    app.add_handler(CallbackQueryHandler(subcategories_callback, pattern=patterns.SUBCATEGORIES))
    app.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=patterns.SELECT_CATEGORY))
    app.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=patterns.BACK_SUBCATEGORY))
    app.add_handler(CallbackQueryHandler(view_task_callback, pattern=callback_data.VIEW_TASKS))
