from calendar import day_name
from datetime import datetime
from collections import defaultdict
from textwrap import dedent

from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, ParseMode)
from telegram.ext import CallbackContext

from bot.database_operations import get_weekly_shifts, get_daily_shifts


def prepare_keyboard() -> InlineKeyboardMarkup:
    """
    Prepare reply keyboard to user.
    """
    keyboard = [
        [
            InlineKeyboardButton(
                "Главное меню",
                callback_data="main_menu"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def prepare_shifts_message(schedule: dict) -> str:
    """
    Prepare message for user with shifts timings.
    """
    message = ""
    for date, shift_timings in schedule.items():
        reformat_shift_timings = "\n".join(shift_timings)
        shift_date = datetime.fromisoformat(date)
        shift_day = day_name[shift_date.weekday()]
        message += dedent(f"""
           🕛 <b>{shift_date.day} {shift_date.strftime("%B")}, {shift_day}</b>
          {reformat_shift_timings}
           -------------------------------""").replace("  ", "")
    return message


def get_shifts_timings(shifts: list) -> dict:
    """
    Return shift timings.
    """
    schedule = defaultdict(list)
    for shift in shifts:
        _, shift_start_time, shift_end_time, shift_date = shift
        shift_timing = f"{shift_start_time} - {shift_end_time}"
        schedule[shift_date].append(shift_timing)
    return dict(schedule)


def get_weekly_schedule(week: str) -> dict:
    """
    Return scheduled shifts on week.
    Variable 'week' can get only one of two parameters: 'current' or 'next'.
    This variable indicates which week function return.
    """
    shifts = get_weekly_shifts(week)
    if not shifts:
        return
    return get_shifts_timings(shifts)


def check_weekly_shifts(update: Update, context: CallbackContext) -> None:
    """
    Return to user shifts on week.
    """
    query = update.callback_query

    week = query.data.split("_")[0]
    weekly_schedule = get_weekly_schedule(week=week)
    if not weekly_schedule:
        query.answer()
        query.edit_message_text(
            text="Пока планируемых смен нет.",
            reply_markup=prepare_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    if week == "current":
        message = """<b>План на эту неделю:</b>\n"""
    else:
        message = """<b>План на следующую неделю:</b>\n"""

    message += prepare_shifts_message(weekly_schedule)
    query.answer()
    query.edit_message_text(
        text=message,
        reply_markup=prepare_keyboard(),
        parse_mode=ParseMode.HTML
    )


def check_daily_shift(update: Update, context: CallbackContext) -> None:
    """
    Return daily shifts.
    """
    shifts = get_daily_shifts()
    query = update.callback_query
    if not shifts:
        query.answer()
        query.edit_message_text(
            text="Сегодня нет запланированных смен.",
            reply_markup=prepare_keyboard(),
            parse_mode=ParseMode.HTML
        )
        return

    schedule = get_shifts_timings(shifts)
    message = "План на сегодня:\n" + prepare_shifts_message(schedule)
    query.answer()
    query.edit_message_text(
        text=message,
        reply_markup=prepare_keyboard(),
        parse_mode=ParseMode.HTML
    )

