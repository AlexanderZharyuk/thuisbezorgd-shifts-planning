from datetime import datetime
from collections import defaultdict
from textwrap import dedent

from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, ParseMode)
from telegram.ext import CallbackContext

from bot.general_functions import get_weekly_shifts


def get_weekly_schedule(week: str) -> dict:
    """
    Return scheduled shifts on week.
    Variable 'week' can get only one of two parameters: 'current' or 'next'.
    This variable indicates which week function return.
    """
    shifts = get_weekly_shifts(week)
    weekly_schedule = defaultdict(list)
    for shift in shifts:
        _, shift_start_time, shift_end_time, shift_date = shift
        shift_timing = f"{shift_start_time} - {shift_end_time}"
        weekly_schedule[shift_date].append(shift_timing)
    return dict(weekly_schedule)


def check_weekly_shifts(update: Update, context: CallbackContext) -> None:
    """
    Return to user shifts on week.
    """
    query = update.callback_query
    keyboard = [
        [
            InlineKeyboardButton(
                "Главное меню",
                callback_data="main_menu"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    week = query.data.split("_")[0]
    weekly_schedule = get_weekly_schedule(week=week)

    if week == "current":
        message = """<b>План на эту неделю:</b>\n"""
    else:
        message = """<b>План на следующую неделю:</b>\n"""

    for date, shift_timings in weekly_schedule.items():
        reformat_shift_timings = "\n".join(shift_timings)
        shift_date = datetime.fromisoformat(date)
        message += dedent(f"""
        🕛 <b>{shift_date.day} {shift_date.strftime("%B")}</b>
        {reformat_shift_timings}
        ------------------------""").replace("  ", "")

    query.answer()
    query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


def check_daily_plan(update: Update, context: CallbackContext) -> None:
    pass
