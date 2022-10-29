import os
from textwrap import dedent

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Посмотреть план на неделю",
                callback_data="weekly_plan"
            ),
        ],
        [
            InlineKeyboardButton(
                "Посмотреть план на сегодня",
                callback_data="daily_plan"
            ),
        ]
    ]

    if update.message.from_user.id == int(os.environ["TELEGRAM_ADMIN_ID"]):
        admin_functionality = [
            [
                InlineKeyboardButton(
                    "💸 Посмотреть ожидаемый доход",
                    callback_data="weekly_income"
                )],
            [
                InlineKeyboardButton(
                    "Добавить смену",
                    callback_data="add_shift"
                ),
                InlineKeyboardButton(
                    "Изменить смену",
                    callback_data="change_shift"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Обновить план на след. неделю",
                    callback_data="update_next_weekly_plan"
                ),
            ]
        ]

        keyboard.extend(admin_functionality)

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = dedent("""
    👋 Привет!
    
    Этот бот поможет тебе узнать, когда смена у Александра. 
    Нажми на кнопку, чтобы узнать план на неделю или же на сегодняшний день.
    """)
    update.message.reply_text(message, reply_markup=reply_markup)
