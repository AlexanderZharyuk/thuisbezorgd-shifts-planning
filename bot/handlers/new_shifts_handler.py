from textwrap import dedent

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from bot.conversation_states import States
from bot.database_operations import update_next_week_shifts


def wait_shifts_from_user(update: Update, context: CallbackContext) -> States:
    """
    Add shifts to the next week.
    """
    user_language = context.user_data.get("user_language")

    if user_language == "RU":
        message = dedent("""
        Отправь расписание смен на следующую неделю в формате:
        
        День-Месяц-Год
        Начало смены - Конец смены
        """)

        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Главное меню",
                        callback_data="main_menu"
                    )
                ]
            ]
        )
    else:
        message = dedent("""
        Send your shifts for next week in format:

        DAY-MONTH-YEAR
        Shift start time - Shift end time
        """)

        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Main menu",
                        callback_data="main_menu"
                    )
                ]
            ]
        )

    callback = update.callback_query
    callback.answer()
    callback.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )
    context.user_data["message_id"] = callback.message.message_id
    context.user_data["chat_id"] = callback.message.chat_id
    return States.WEEKLY_SHIFTS


def update_shifts(update: Update, context: CallbackContext) -> None:
    """
    Update shifts plan.
    """
    user_language = context.user_data.get("user_language")

    if user_language == "RU":
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Главное меню",
                        callback_data="main_menu"
                    )
                ]
            ]
        )
        try:
            update_next_week_shifts(update.message.text)
        # TODO Localize exception
        except Exception as error:
            update.message.reply_text(f"Возникла ошибка. Попробуй снова.")
        else:
            context.bot.delete_message(
                chat_id=context.user_data.get("chat_id"),
                message_id=context.user_data.get("message_id")
            )
            context.bot.delete_message(
                chat_id=context.user_data.get("chat_id"),
                message_id=update.message.message_id
            )
            message = update.message.reply_text(
                dedent("""
                Смены были успешно занесены в БД.
                """),
                reply_markup=reply_markup
            )
            context.user_data["message_id"] = message.message_id
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Main menu",
                        callback_data="main_menu"
                    )
                ]
            ]
        )
        try:
            update_next_week_shifts(update.message.text)
        # TODO Localize exception
        except Exception as error:
            update.message.reply_text(f"Error. Try again please.")
        else:
            context.bot.delete_message(
                chat_id=context.user_data.get("chat_id"),
                message_id=context.user_data.get("message_id")
            )
            context.bot.delete_message(
                chat_id=context.user_data.get("chat_id"),
                message_id=update.message.message_id
            )
            message = update.message.reply_text(
                dedent("""
                        Shifts was successfully added to database.
                        """),
                reply_markup=reply_markup
            )
            context.user_data["message_id"] = message.message_id
