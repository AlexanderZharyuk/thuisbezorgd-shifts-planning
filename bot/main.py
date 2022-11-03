import os
import sqlite3

from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,
                          ConversationHandler, MessageHandler, Filters)

from handlers.main_menu_handler import start, States
from handlers.check_shifts_handlers import (check_weekly_shifts,
                                            check_daily_shift)
from handlers.new_shifts_handlers import wait_shifts_from_user, update_shifts
from handlers.weekly_income_handler import show_weekly_income


def main() -> None:
    load_dotenv()
    telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    database_name = os.environ["DATABASE_NAME"]

    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shifts
        ([shift_id] INTEGER PRIMARY KEY AUTOINCREMENT,
         [shift_time_starts] TEXT, 
        [shift_time_ends] TEXT, [shift_date] TEXT)
    """)
    connection.commit()

    updater = Updater(telegram_bot_token)

    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            check_weekly_shifts,
            pattern="current_week_shifts"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            check_weekly_shifts,
            pattern="next_week_shifts"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(
            check_daily_shift,
            pattern="daily_plan"
        )
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(start, pattern="main_menu")
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(show_weekly_income, pattern="weekly_income")
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", start)
        ],
        states={
            States.CHOOSING: [
                CallbackQueryHandler(
                    wait_shifts_from_user,
                    pattern="update_next_weekly_plan"
                )
            ],
            States.WEEKLY_SHIFTS: [
                CallbackQueryHandler(
                    start,
                    pattern="main_menu"
                ),
                MessageHandler(
                    Filters.text, update_shifts
                ),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), None)],
        name="conversation",
        allow_reentry=True,
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
