import os
import sqlite3

from datetime import datetime
from collections import defaultdict
from typing import NamedTuple

from telegram import Update
from telegram.ext import CallbackContext

from common_functions import calculate_weekdays


class User(NamedTuple):
    telegram_id: int
    language: str


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
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users
            ([user_id] INTEGER PRIMARY KEY AUTOINCREMENT,
             [telegram_id] INT, 
             [language] TEXT)
        """)
    connection.commit()
    connection.close()


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


def check_user_in_database(telegram_id: int) -> bool | None:
    """
    Check user in DB by telegram ID.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = f"""
        SELECT * FROM users
        WHERE telegram_id == '{telegram_id}'
    """
    sql_query = cursor.execute(query)
    user = sql_query.fetchone()
    connection.close()
    return True if user is not None else user


def save_user_to_database(telegram_id: int) -> None:
    """
    Save user to DB.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = """
        INSERT INTO users(telegram_id) VALUES (?)
    """

    cursor.execute(query, (telegram_id, ))
    connection.commit()
    connection.close()


def get_user_language(telegram_id: int) -> str | None:
    """
    Get user language from DB.
    """
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = f"""
            SELECT telegram_id, language FROM users
            WHERE telegram_id = '{telegram_id}'
        """

    sql_query = cursor.execute(query)
    user_info = sql_query.fetchone()
    user = User(telegram_id=user_info[0], language=user_info[1])
    connection.close()
    return user.language


def add_language_to_user(telegram_id: int, language: str) -> None:
    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = f"""
                UPDATE users
                SET language = '{language}'
                WHERE telegram_id = '{telegram_id}'
            """

    cursor.execute(query)
    connection.commit()
    connection.close()


def change_user_language(update: Update, context: CallbackContext):
    """
    Change user prefer language.
    """
    from handlers.main_menu_handler import greeting_block, States

    language_code = context.user_data.get("user_language")
    new_language = "EN" if language_code == "RU" else "RU"
    callback = update.callback_query
    telegram_id = callback.from_user.id
    context.user_data["user_language"] = new_language

    database_name = os.environ["DATABASE_NAME"]
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    query = f"""
                UPDATE users
                SET language = '{new_language}'
                WHERE telegram_id = '{telegram_id}'
            """

    cursor.execute(query)
    connection.commit()
    connection.close()

    greeting_block(update, context)
    return States.CHOOSING
