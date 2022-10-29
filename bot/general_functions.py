import os
import sqlite3

from datetime import datetime, timedelta


def get_weekly_shifts(week: str) -> list[set]:
    """
    Return weekly shift from database.
    Variable 'week' can get only one of two parameters: 'current' or 'next'.
    This variable indicates which week function return.
    """
    today = datetime.today()
    if week == "current":
        date_of_week_beginning = today - timedelta(days=today.weekday())
        date_of_week_ending = date_of_week_beginning + timedelta(days=6)
    elif week == "next":
        today = datetime(2022, 11, 2)
        day_number = today.weekday()
        if not day_number:
            date_of_week_beginning = today
        else:
            date_of_week_beginning = today + timedelta(days=7 - day_number)

        date_of_week_ending = date_of_week_beginning + timedelta(days=6)

    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = f"""
    SELECT * FROM shifts
    WHERE shift_date BETWEEN '{date_of_week_beginning.date()}'
    AND '{date_of_week_ending.date()}'
    ORDER BY shift_date
    """
    cursor.execute(query)
    return cursor.fetchall()


def get_daily_shifts() -> str:
    """
    Return daily shift info.
    """
    # database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect("shifts.sqlite3")
    cursor = connection.cursor()

    today = datetime.today()

    query = f"""
    SELECT * FROM shifts
    WHERE shift_date = '{today.date()}'
    """
    cursor.execute(query)
    return cursor.fetchall()