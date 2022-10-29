import os
import sqlite3

from datetime import datetime, timedelta


def get_current_weekly_shifts() -> list[set]:
    today = datetime.today()
    date_of_week_beginning = today - timedelta(days=today.weekday())
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

