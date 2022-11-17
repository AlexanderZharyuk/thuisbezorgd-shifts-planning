from textwrap import dedent

from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, ParseMode)
from telegram.ext import CallbackContext

from bot.conversation_states import States
from bot.database_operations import (get_future_shifts, get_shifts_on_day,
                                     delete_shifts_on_day,
                                     change_shifts_timings)


def choose_shift_day_for_change(
        update: Update,
        context: CallbackContext) -> States:
    """
    Return the message with shifts days in InlineKeyboard to user.
    """
    message = dedent("""
    Выбери дату смены, которую хотел бы изменить.
    """)
    future_shifts = get_future_shifts()
    keyboard = [
        [
            InlineKeyboardButton(f"{date[0]}", callback_data=date[0])
        ] for date in future_shifts
    ]
    keyboard.append(
        [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    callback = update.callback_query
    callback.answer()
    callback.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML,
    )

    return States.CHOOSE_SHIFT


def choose_shift_for_change(update: Update, context: CallbackContext) -> States:
    """
    Answer to user message with shifts in inline keyboard.
    """
    callback = update.callback_query
    date = callback.data
    shifts = get_shifts_on_day(date)
    shifts_on_this_date = [f"<b>{time[0]} - {time[1]}</b>" for time in shifts]
    reformat_shifts = "\n".join(shifts_on_this_date)

    message = dedent(f"""
    В этот день будут следующие смены:
    {reformat_shifts}
    
    Отправьте измененные смены для того, чтобы скорректировать расписание.
    """).replace("  ", "")

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Удалить смены из расписания",
                    callback_data="delete"
                )
            ],
            [
                InlineKeyboardButton(
                    "Назад к просмотру смен",
                    callback_data="cancel"
                )
            ],
            [
                InlineKeyboardButton(
                    "Главное меню",
                    callback_data="main_menu"
                )
            ],
        ]
    )

    callback.answer()
    callback.edit_message_text(
        text=message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    context.user_data["message_id"] = callback.message.message_id
    context.user_data["chat_id"] = callback.message.chat_id
    context.user_data["shifts_date"] = date
    return States.CHANGE_SHIFT


def delete_shifts(update: Update, context: CallbackContext):
    """
    Delete shifts from database.
    """
    shifts_date = context.user_data.get("shifts_date")
    delete_shifts_on_day(date=shifts_date)
    message = dedent("""
    Смены были успешно удалены из БД.
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
    callback = update.callback_query
    callback.answer()
    callback.edit_message_text(
        text=message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup

    )


def change_shifts(update: Update, context: CallbackContext):
    """
    Change shift timings in database.
    """
    context.bot.delete_message(
        chat_id=context.user_data.get("chat_id"),
        message_id=context.user_data.get("message_id")
    )
    context.bot.delete_message(
        chat_id=context.user_data.get("chat_id"),
        message_id=update.message.message_id
    )
    new_timings = update.message.text
    date = context.user_data["shifts_date"]
    change_shifts_timings(date=date, new_timing=new_timings)

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
    update.message.reply_text(
        "Смены на этот день были обновлены.",
        reply_markup=reply_markup
    )
