import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler
from telegram.ext.filters import StatusUpdate

from src.bot.constants import callback_data, commands
from src.bot.keyboards import feedback_buttons, get_confirm_keyboard, get_start_keyboard
from src.bot.services.external_site_user import ExternalSiteUserService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message
from src.core.logging.utils import logger_decor


@logger_decor
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ext_user_service = ExternalSiteUserService()
    ext_user = await ext_user_service.get_ext_user_by_args(context.args)
    user_service = UserService()
    if ext_user is not None:
        await user_service.register_user(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=ext_user.first_name,
            last_name=ext_user.last_name,
            email=ext_user.email,
            external_id=ext_user.id,
        )
        await user_service.set_categories_to_user(update.effective_user.id, ext_user.specializations)
        keyboard_feedback = await feedback_buttons(
            ext_user.first_name,
            ext_user.last_name,
            ext_user.email,
            )
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Обратная связь - через кнопки под клавиатурой будут всегда под рукой!",
            reply_markup=keyboard_feedback,
        )
    else:
        await user_service.register_user(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        )
        keyboard_feedback = await feedback_buttons(
            update.effective_user.first_name,
            update.effective_user.last_name,
            None)
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Обратная связь - через кнопки под клавиатурой будут всегда под рукой!",
            reply_markup=keyboard_feedback,
        )
    categories = await user_service.get_user_categories(update.effective_user.id)
    callback_data_on_start = commands.GREETING_REGISTERED_USER if categories else callback_data.CHANGE_CATEGORY
    keyboard = await get_start_keyboard(callback_data_on_start=callback_data_on_start)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Привет! 👋 \n\n"
        'Я бот платформы интеллектуального волонтерства <a href="https://procharity.ru/">ProCharity</a>. '
        "Буду держать тебя в курсе новых задач и помогу "
        "оперативно связаться с командой поддержки.\n\n",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@logger_decor
@delete_previous_message
async def confirm_chosen_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_confirm_keyboard()

    user_service = UserService()
    categories = await user_service.get_user_categories(update.effective_user.id)
    context.user_data["selected_categories"] = {category: None for category in categories}
    text = ", ".join(categories.values())

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Вот список твоих профессиональных компетенций: *{text}* Все верно?",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


@logger_decor
async def web_app_data(update: Update):
    user_data = json.loads(update.effective_message.web_app_data.data)
    buttons = [
        [InlineKeyboardButton(text="Открыть меню", callback_data=callback_data.MENU)],
        [InlineKeyboardButton(text="Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        text=f"Спасибо, я передал информацию команде ProCharity! Ответ придет на почту {user_data['email']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        text="Вы можете вернуться в меню или посмотреть открытые задания. Нажмите на нужную кнопку.",
        reply_markup=keyboard,
    )


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
    app.add_handler(CallbackQueryHandler(confirm_chosen_categories, pattern=commands.GREETING_REGISTERED_USER))
    app.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))
