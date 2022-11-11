from collections import defaultdict

from bot.database_operations import get_weekly_shifts


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
