import os
import sqlite3

from datetime import datetime, timedelta
from collections import defaultdict


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


def _parse_shifts_text(text: str) -> dict:
    """
    Parse text from user to dict-format.
    """
    shifts = text.split("\n")
    schedule = defaultdict(list)

    for shift in shifts:
        if not shift:
            continue

        if len(shift.split("-")) > 2:
            shift_day = datetime.strptime(
                shift.replace(":", ""),
                "%d-%m-%Y"
            ).date()
            continue

        schedule[shift_day].append(shift)

    return dict(schedule)


def get_weekly_shifts(week: str) -> list[set]:
    """
    Return weekly shift from database.
    Variable 'week' can get only one of three parameters: 'current', 'next' or
    'previous'.
    This variable indicates which week function return.
    """
    date_of_week_beginning, date_of_week_ending = calculate_weekdays(week)

    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = f"""
    SELECT * FROM shifts
    WHERE shift_date BETWEEN '{date_of_week_beginning}'
    AND '{date_of_week_ending}'
    ORDER BY shift_date
    """
    cursor.execute(query)
    return cursor.fetchall()


def get_daily_shifts() -> str:
    """
    Return daily shift info.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    today = datetime.today()

    query = f"""
    SELECT * FROM shifts
    WHERE shift_date = '{today.date()}'
    """
    cursor.execute(query)
    return cursor.fetchall()


def update_next_week_shifts(text: str):
    """
    Record to DB shifts on next week.
    """
    schedule = _parse_shifts_text(text)
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    shifts = []
    for shift_date, shift_timings in schedule.items():
        for time in shift_timings:
            shift_start, shift_end = time.split(" - ")
            shift_info = (shift_date, shift_start, shift_end)
            shifts.append(shift_info)

    query = f"""
        INSERT INTO shifts(
         shift_date,
         shift_time_starts,
         shift_time_ends
         ) VALUES (?, ?, ?)
        """
    cursor.executemany(query, shifts)
    connection.commit()
