from collections import defaultdict
from datetime import datetime, timedelta


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
    from bot.database_operations import get_weekly_shifts

    shifts = get_weekly_shifts(week)
    if not shifts:
        return
    return get_shifts_timings(shifts)


def calculate_weekdays(week: str) -> tuple[datetime, datetime]:
    """
    Calculate week beginning and starting dates.
    """
    today = datetime.today()
    if week == "current":
        date_of_week_beginning = today - timedelta(days=today.weekday())
        date_of_week_ending = date_of_week_beginning + timedelta(days=6)
    elif week == "next":
        day_number = today.weekday()
        if not day_number:
            date_of_week_beginning = today + timedelta(days=7)
        else:
            date_of_week_beginning = today + timedelta(days=7 - day_number)
        date_of_week_ending = date_of_week_beginning + timedelta(days=6)
    elif week == "previous":
        day_number = today.weekday()
        if not day_number:
            date_of_week_beginning = today - timedelta(days=7)
        else:
            date_of_week_beginning = today - timedelta(days=7 + day_number)
        date_of_week_ending = date_of_week_beginning + timedelta(days=6)

    return date_of_week_beginning.date(), date_of_week_ending.date()
