from dependency_injector.wiring import Provide
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CallbackQueryHandler

from src.bot.constants import callback_data
from src.bot.keyboards import get_back_menu, get_task_info_keyboard, tasks_again_get_back_menu, view_more_tasks_keyboard
from src.bot.services.task import TaskService
from src.bot.utils import delete_previous_message
from src.core.depends import Container
from src.core.logging.utils import logger_decor
from src.core.messages import display_task


@logger_decor
@delete_previous_message
async def view_task_callback(
    update: Update,
    context: CallbackContext,
    limit: int = 3,
    task_service: TaskService = Provide[Container.bot_services_container.bot_task_service],
):
    telegram_id = context._user_id
    page_number = context.user_data.get("page_number", 1)
    viewed_all = context.user_data.get("viewed_all", False)
    if viewed_all:
        keyboard = await tasks_again_get_back_menu()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Ты просмотрел все актуальные задания на сегодня.",
            reply_markup=keyboard,
        )
        return

    tasks_to_show, offset, page_number = await task_service.get_user_tasks_by_page(
        page_number,
        limit,
        telegram_id,
    )

    if not tasks_to_show and page_number == 1:
        keyboard = await get_back_menu()
        keyboard = await tasks_again_get_back_menu()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Актуальных заданий по твоим компетенциям на сегодня нет.",
            reply_markup=keyboard,
        )
        context.user_data["viewed_all"] = True
        return

    for task in tasks_to_show:
        message = display_task(task)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=get_task_info_keyboard(task),
        )

    remaining_tasks = await task_service.get_remaining_user_tasks_count(limit, offset, telegram_id)
    await show_next_tasks(update, context, page_number, remaining_tasks)


async def show_next_tasks(update: Update, context: CallbackContext, page_number: int, remaining_tasks: int):
    if remaining_tasks > 0:
        text = f"Есть ещё задания, показать? Осталось: {remaining_tasks}"
        context.user_data["page_number"] = page_number + 1
        keyboard = await view_more_tasks_keyboard()
    else:
        text = "Ты просмотрел все актуальные задания на сегодня."
        keyboard = await get_back_menu()
        context.user_data["viewed_all"] = True

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard,
    )


async def view_tasks_again_callback(
    update: Update,
    context: CallbackContext,
):
    context.user_data["viewed_all"] = False
    context.user_data["page_number"] = 1
    await view_task_callback(
        update, context, limit=3, task_service=Provide[Container.bot_services_container.bot_task_service]
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(view_tasks_again_callback, pattern=callback_data.VIEW_TASKS_AGAIN))
    app.add_handler(CallbackQueryHandler(view_task_callback, pattern=callback_data.VIEW_TASKS))
