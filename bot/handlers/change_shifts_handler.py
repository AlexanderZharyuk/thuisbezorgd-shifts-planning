from textwrap import dedent

from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, ParseMode)
from telegram.ext import CallbackContext

from bot.conversation_states import States
from bot.database_operations import (get_future_shifts, get_shifts_on_day,
                                     delete_shifts_on_day,
                                     change_shifts_timings, get_user_language)


def _russian_keyboard() -> InlineKeyboardMarkup:
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
    return reply_markup


def _english_keyboard() -> InlineKeyboardMarkup:
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Delete shifts from schedule",
                    callback_data="delete"
                )
            ],
            [
                InlineKeyboardButton(
                    "Back to shifts",
                    callback_data="cancel"
                )
            ],
            [
                InlineKeyboardButton(
                    "Main menu",
                    callback_data="main_menu"
                )
            ],
        ]
    )
    return reply_markup


def choose_shift_day_for_change(
        update: Update,
        context: CallbackContext) -> States:
    """
    Return the message with shifts days in InlineKeyboard to user.
    """

    future_shifts = get_future_shifts()
    keyboard = [
        [
            InlineKeyboardButton(f"{date[0]}", callback_data=date[0])
        ] for date in future_shifts
    ]

    callback = update.callback_query
    user_language = context.user_data.get("user_language")

    if user_language == "RU":
        message = dedent("""
            Выбери дату смены, которую хотел бы изменить.
            """)
        keyboard.append(
            [InlineKeyboardButton("Главное меню", callback_data="main_menu")]
        )
    else:
        message = dedent("""
            Choose the date when you want to change shifts.
            """)
        keyboard.append(
            [InlineKeyboardButton("Main menu", callback_data="main_menu")]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)

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

    user_language = context.user_data.get("user_language")
    if user_language == "RU":
        message = dedent(f"""
        В этот день будут следующие смены:
        {reformat_shifts}
        
        Отправьте измененные смены для того, чтобы скорректировать расписание.
        """).replace("  ", "")
        reply_markup = _russian_keyboard()
    else:
        message = dedent(f"""
        At this day will be these shifts:
        {reformat_shifts}
        
        Send correct shifts if you want to change this schedule.
        """). replace("  ", "")
        reply_markup = _english_keyboard()

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
    callback = update.callback_query

    user_language = context.user_data.get("user_language")
    if user_language == "RU":
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
    else:
        message = dedent("""
        Shifts was successfully deleted from database.
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
        update.message.reply_text(
            "Смены на этот день были обновлены.",
            reply_markup=reply_markup
        )
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
        update.message.reply_text(
            "This day shifts was successfully updated.",
            reply_markup=reply_markup
        )
