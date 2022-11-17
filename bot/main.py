import os

from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,
                          ConversationHandler, MessageHandler, Filters)

from database_operations import create_database
from handlers.main_menu_handler import start, States
from handlers.check_shifts_handler import (check_weekly_shifts,
                                           check_daily_shift)
from handlers.new_shifts_handler import wait_shifts_from_user, update_shifts
from handlers.weekly_income_handler import show_weekly_income
from handlers.change_shifts_handler import (choose_shift_day_for_change,
                                            choose_shift_for_change,
                                            delete_shifts, change_shifts)


def main() -> None:
    load_dotenv()
    telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    database_name = os.environ["DATABASE_NAME"]
    create_database(database_name=database_name)

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
        CallbackQueryHandler(show_weekly_income, pattern="weekly_income")
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(start, pattern="main_menu")
        ],
        states={
            States.CHOOSING: [
                CallbackQueryHandler(
                    wait_shifts_from_user,
                    pattern="update_next_weekly_plan"
                ),
                CallbackQueryHandler(
                    choose_shift_day_for_change,
                    pattern="change_shift"
                )
            ],
            States.WEEKLY_SHIFTS: [
                MessageHandler(
                    Filters.text, update_shifts
                ),
            ],
            States.CHOOSE_SHIFT: [
                CallbackQueryHandler(
                    choose_shift_for_change
                )
            ],
            States.CHANGE_SHIFT: [
                CallbackQueryHandler(
                    delete_shifts,
                    pattern="delete"
                ),
                CallbackQueryHandler(
                    choose_shift_day_for_change,
                    pattern="cancel"
                ),
                MessageHandler(
                    Filters.text, change_shifts
                )
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
