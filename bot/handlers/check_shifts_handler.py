from calendar import day_name
from datetime import datetime
from textwrap import dedent

from telegram import (Update, InlineKeyboardButton,
                      InlineKeyboardMarkup, ParseMode)
from telegram.ext import CallbackContext

from bot.database_operations import get_daily_shifts, get_user_language
from bot.common_functions import get_weekly_schedule, get_shifts_timings


def _prepare_keyboard(
        update: Update,
        context: CallbackContext) -> InlineKeyboardMarkup:
    """
    Prepare reply keyboard to user.
    """

    user_language = context.user_data.get("user_language")
    if not user_language:
        user_language = get_user_language(update.callback_query.from_user.id)

    if user_language == "RU":
        keyboard = [
            [
                InlineKeyboardButton(
                    "Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    "Main menu",
                    callback_data="main_menu"
                )
            ]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def _prepare_shifts_message(schedule: dict) -> str:
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


def check_weekly_shifts(update: Update, context: CallbackContext) -> None:
    """
    Return to user shifts on week.
    """
    query = update.callback_query

    user_language = context.user_data.get("user_language")
    if not user_language:
        user_language = get_user_language(update.callback_query.from_user.id)

    week = query.data.split("_")[0]
    weekly_schedule = get_weekly_schedule(week=week)
    if not weekly_schedule:
        if user_language == "RU":
            message = "Пока планируемых смен нет."
        else:
            message = "No shifts in plan for current week."
        query.answer()
        query.edit_message_text(
            text=message,
            reply_markup=_prepare_keyboard(update, context),
            parse_mode=ParseMode.HTML
        )
        return

    if user_language == "RU":
        if week == "current":
            message = """<b>План на эту неделю:</b>\n"""
        else:
            message = """<b>План на следующую неделю:</b>\n"""
    else:
        if week == "current":
            message = """<b>Plan for current week:</b>\n"""
        else:
            message = """<b>Plan for next week:</b>\n"""

    message += _prepare_shifts_message(weekly_schedule)
    query.answer()
    query.edit_message_text(
        text=message,
        reply_markup=_prepare_keyboard(update, context),
        parse_mode=ParseMode.HTML
    )


def check_daily_shift(update: Update, context: CallbackContext) -> None:
    """
    Return daily shifts.
    """
    query = update.callback_query
    user_language = context.user_data.get("user_language")
    if not user_language:
        user_language = get_user_language(update.callback_query.from_user.id)

    shifts = get_daily_shifts()
    if not shifts:
        if user_language == "RU":
            message = "Сегодня нет запланированных смен."
        else:
            message = "No shifts in plan today."
        query.answer()
        query.edit_message_text(
            text=message,
            reply_markup=_prepare_keyboard(update, context),
            parse_mode=ParseMode.HTML
        )
        return

    schedule = get_shifts_timings(shifts)

    if user_language == "RU":
        message = "План на сегодня:\n" + _prepare_shifts_message(schedule)
    else:
        message = "Plan for today:\n" + _prepare_shifts_message(schedule)
    query.answer()
    query.edit_message_text(
        text=message,
        reply_markup=_prepare_keyboard(update, context),
        parse_mode=ParseMode.HTML
    )

