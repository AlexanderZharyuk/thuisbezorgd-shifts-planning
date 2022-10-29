import os

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler

from handlers.main_menu_handler import start


def main() -> None:
    load_dotenv()
    telegram_bot_token = os.environ["TELEGRAM_BOT_TOKEN"]

    updater = Updater(telegram_bot_token)

    updater.dispatcher.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
