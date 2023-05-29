import json
import urllib

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      Update, WebAppInfo, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, KeyboardButton)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackContext

from src.bot.constants import commands, callback_data, keyboards_const
from src.bot.keyboards import get_categories_keyboard, get_subcategories_keyboard, MENU_KEYBOARD
from src.core.services.user import UserService
from src.settings import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    await user_service.register_user(
        telegram_id=update.effective_chat.id,
        username=update.effective_chat.username,
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=keyboards_const.START_TEXT,
                    callback_data=commands.GREETING,
                )
            ]
        ]
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=keyboards_const.WELCOME_TEXT,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


async def menu_callback(update: Update, context: CallbackContext):
    """Create button menu."""
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        keyboards_const.SELECT_INTERESTING_TEXT,
        reply_markup=reply_markup
    )


async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["parent_id"] = None
    await update.message.reply_text(
        keyboards_const.SELECT_COMPETITIONS_TEXT,
        reply_markup=await get_categories_keyboard(),
    )


async def ask_your_question(update: Update, context: CallbackContext):
    name = update.effective_chat["first_name"]
    surname = update.effective_chat["last_name"]
    text = keyboards_const.ASK_QUESTION_TEXT
    params = {'name': name, 'surname': surname}
    if update.effective_message.web_app_data:
        text = keyboards_const.FIX_DATA_TEXT
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=keyboards_const.PUSH_QUESTION_BUTTON_TEXT,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(
                    url=f"{settings.feedback_form_template_url}?{urllib.parse.urlencode(params)}"
                )
            )
        ),
    )


async def web_app_data(update: Update, context: CallbackContext):
    user_data = json.loads(update.effective_message.web_app_data.data)
    buttons = [
        [
            InlineKeyboardButton(
                text=keyboards_const.OPEN_IN_MENU_TEXT,
                callback_data=callback_data.MENU
            )
        ],
        [
            InlineKeyboardButton(
                text=keyboards_const.VIEW_OPEN_TASKS_TEXT,
                callback_data=callback_data.VIEW_TASKS
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        text=f"Спасибо, я передал информацию команде ProCharity!"
             f"Ответ придет на почту {user_data['email']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        text=keyboards_const.BACK_MENU_VIEW_OPEN_TASKS_TEXT,
        reply_markup=keyboard,
    )


async def subcategories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parent_id = int(context.match.group(1))
    context.user_data["parent_id"] = parent_id

    await query.message.edit_text(
        keyboards_const.SELECT_COMPETITIONS_TEXT,
        reply_markup=await get_subcategories_keyboard(parent_id, context),
    )


async def select_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    subcategory_id = int(context.match.group(1))
    selected_categories = context.user_data.setdefault("selected_categories", {})

    if subcategory_id not in selected_categories:
        selected_categories[subcategory_id] = None
    else:
        del selected_categories[subcategory_id]

    parent_id = context.user_data["parent_id"]

    await query.message.edit_text(
        keyboards_const.SELECT_COMPETITIONS_TEXT,
        reply_markup=await get_subcategories_keyboard(parent_id, context),
    )


async def back_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.message.edit_text(
        keyboards_const.SELECT_COMPETITIONS_TEXT,
        reply_markup=await get_categories_keyboard(),
    )
