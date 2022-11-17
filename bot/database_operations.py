import os
import sqlite3

from datetime import datetime, timedelta
from collections import defaultdict


def create_database(database_name: str) -> None:
    """
    Create database if that not exist in folder.
    """
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS shifts
            ([shift_id] INTEGER PRIMARY KEY AUTOINCREMENT,
             [shift_time_starts] TEXT, 
            [shift_time_ends] TEXT, [shift_date] TEXT)
        """)
    connection.commit()
    connection.close()


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


def get_weekly_shifts(week: str) -> list[tuple]:
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
    weekly_shifts = cursor.fetchall()
    connection.close()
    return weekly_shifts


def get_daily_shifts() -> str:
    """
    Return daily shift info.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    today_date = datetime.today().date()

    query = f"""
    SELECT * FROM shifts
    WHERE shift_date = '{today_date}'
    """
    cursor.execute(query)
    daily_shifts = cursor.fetchall()
    connection.close()
    return daily_shifts


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
    connection.close()


def get_future_shifts() -> list[tuple]:
    """
    Return future shifts.
    """
    today_date = datetime.today().date()
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    query = f"""
        SELECT DISTINCT shift_date FROM shifts
        WHERE shift_date >= '{today_date}'
        ORDER BY shift_date
    """
    cursor.execute(query)
    future_shifts = cursor.fetchall()
    connection.close()
    return future_shifts


def get_shifts_on_day(date: str) -> list[tuple]:
    """
    Return list with shift on day from database.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    query = f"""
            SELECT shift_time_starts, shift_time_ends FROM shifts
            WHERE shift_date = '{date}'
        """
    cursor.execute(query)
    shifts = cursor.fetchall()
    connection.close()
    return shifts


def delete_shifts_on_day(date: str):
    """
    Delete shifts on day from database.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    query = f"""
               DELETE FROM shifts
               WHERE shift_date = '{date}'
           """
    cursor.execute(query)
    connection.commit()
    connection.close()


def change_shifts_timings(date: str, new_timing: str):
    """
    Change shifts timings in database.
    """
    delete_shifts_on_day(date)
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    shift_timings = new_timing.split("\n")
    new_shift_timings = []
    for time in shift_timings:
        shift_start_time, shift_end_time = time.split(" - ")
        new_shift_timings.append((date, shift_start_time, shift_end_time))

    query = f"""
            INSERT INTO shifts(
             shift_date,
             shift_time_starts,
             shift_time_ends
             ) VALUES (?, ?, ?)
            """
    cursor.executemany(query, new_shift_timings)
    connection.commit()
    connection.close()

