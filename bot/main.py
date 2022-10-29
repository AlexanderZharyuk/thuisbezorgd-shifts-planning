import os
import sqlite3

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from handlers.main_menu_handler import start
from handlers.check_plan_handlers import check_weekly_plan


def main() -> None:
    load_dotenv()
    telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    database_name = os.environ["DATABASE_NAME"]

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts
        ([shift_id] INTEGER PRIMARY KEY, [shift_time_starts] TEXT, 
        [shift_time_ends] TEXT, [shift_date] TEXT)
    """)
    connection.commit()

    updater = Updater(telegram_bot_token)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(
        CallbackQueryHandler(check_weekly_plan, pattern="weekly_plan")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(start, pattern="main_menu")
    )

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
