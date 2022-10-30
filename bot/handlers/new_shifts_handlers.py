from textwrap import dedent

from telegram import Update
from telegram.ext import CallbackContext

from bot.conversation_states import States
from bot.general_functions import update_next_week_shifts


def wait_shifts_from_user(update: Update, context: CallbackContext) -> States:
    """
    Add shifts to the next week.
    """
    message = dedent("""
    Отправь расписание смен на следующую неделю в формате:
    
    День-Месяц-Год
    Начало смены - Конец смены
    
    Для отмены - нажмите команду /start
    """)

    callback = update.callback_query
    callback.answer()
    callback.edit_message_text(
        text=message,
    )
    context.user_data["message_id"] = callback.message.message_id
    context.user_data["chat_id"] = callback.message.chat_id
    return States.WEEKLY_SHIFTS


def update_shifts(update: Update, context: CallbackContext) -> None:
    context.bot.delete_message(
        chat_id=context.user_data.get("chat_id"),
        message_id=context.user_data.get("message_id")
    )
    context.bot.delete_message(
        chat_id=context.user_data.get("chat_id"),
        message_id=update.message.message_id
    )
    try:
        update_next_week_shifts(update.message.text)
    except Exception as error:
        # TODO локализовать ошибку для подробного ответа
        update.message.reply_text(f"Возникла ошибка: {error}")
    else:
        message = update.message.reply_text(
            dedent("""
            Смены были занесены в БД.
            
            Нажми /start чтобы оказаться в главном меню.
            """)
        )
        context.user_data["message_id"] = message.message_id
