import os
from textwrap import dedent
from datetime import datetime, date, time

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from bot.database_operations import get_weekly_shifts, calculate_weekdays
from bot.handlers.check_shifts_handlers import get_shifts_timings


def _parse_hours_per_shift(shift_timings: list) -> int:
    """
    Convert shift date from string to int format.
    """
    hours_per_day = 0
    for shift_time in shift_timings:
        shift_start_time, shift_end_time = shift_time.split(" - ")
        shift_start_hour, shift_start_minute = shift_start_time.split(":")
        shift_end_hour, shift_end_minute = shift_end_time.split(":")

        shift_start_time_in_datetime = time(
            hour=int(shift_start_hour),
            minute=int(shift_start_minute)
        )
        shift_end_time_in_datetime = time(
            hour=int(shift_end_hour),
            minute=int(shift_end_minute)
        )
        duration = datetime.combine(date.min, shift_end_time_in_datetime) - \
                   datetime.combine(date.min, shift_start_time_in_datetime)

        hours_per_day += duration.seconds / 3600

    return hours_per_day


def _calculate_weekly_income() -> tuple:
    """
    Calculate income with shifts timings from DB.
    """
    current_week_shifts = get_weekly_shifts(week="current")
    previous_week_shifts = get_weekly_shifts(week="previous")

    current_week_shifts_timings = get_shifts_timings(current_week_shifts)
    previous_week_shifts_timings = get_shifts_timings(previous_week_shifts)

    hours_per_current_week = 0
    for shift_times in current_week_shifts_timings.values():
        hours_per_current_week += _parse_hours_per_shift(shift_times)

    hours_per_previous_week = 0
    for shift_times in previous_week_shifts_timings.values():
        hours_per_previous_week += _parse_hours_per_shift(shift_times)

    salary_rate = int(os.environ["RATE_PER_HOUR"])
    tax_percent = int(os.environ["TAX_PERCENT"]) / 100

    salary_without_tax = salary_rate * hours_per_current_week
    current_week_income = salary_without_tax - (salary_rate * tax_percent)

    salary_without_tax = salary_rate * hours_per_previous_week
    previous_week_income = salary_without_tax - (salary_rate * tax_percent)

    current_week_income = 0 if current_week_income < 0 else current_week_income
    previous_week_income = 0 if previous_week_income < 0 else previous_week_income

    return current_week_income, previous_week_income


def show_weekly_income(update: Update, context: CallbackContext) -> None:
    """
    Calculate previous and current week income and show this to user.
    """
    callback = update.callback_query
    callback.answer()

    current_week_beginning, current_week_ending = calculate_weekdays(
        week="current"
    )
    previous_week_beginning, previous_week_ending = calculate_weekdays(
        week="previous"
    )
    current_week_income, previous_week_income = _calculate_weekly_income()
    message = dedent(f"""
    💸 Ожидаемый доход (С вычетом налогов):
    
    За текущую неделю
    <b>{current_week_beginning.day} {current_week_beginning.strftime("%B")} - \
    {current_week_ending.day} {current_week_ending.strftime("%B")}</b>: \
    {current_week_income} EUR.
    
    За предыдущую неделю
    <b>{previous_week_beginning.day} {previous_week_beginning.strftime("%B")} \
     - {previous_week_ending.day} {previous_week_ending.strftime("%B")}</b>: \
    {previous_week_income} EUR.
    
    Чтобы вернуться в меню - напишите /menu.
    """).replace("  ", "")

    context.user_data["message_id"] = callback.message.message_id
    context.user_data["chat_id"] = callback.message.chat_id

    callback.edit_message_text(
        text=message,
        parse_mode=ParseMode.HTML
    )

