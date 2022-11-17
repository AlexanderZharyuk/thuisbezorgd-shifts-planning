import os

from textwrap import dedent

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# TODO Try to fix it later.
import sys
sys.path.append(".")

from bot.conversation_states import States


def start(update: Update, context: CallbackContext) -> States:
    callback = update.callback_query
    if callback:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.message.from_user.id

    keyboard = [
        [
            InlineKeyboardButton(
                "💥 Эта неделя",
                callback_data="current_week_shifts"
            ),
            InlineKeyboardButton(
                "⏭️ Следующая неделя",
                callback_data="next_week_shifts"
            ),
        ],
        [
            InlineKeyboardButton(
                "📅 План на сегодня",
                callback_data="daily_plan"
            ),
        ]
    ]

    if user_id == int(os.environ["MODERATORS_TELEGRAM_ID"]):
        moderators_functionality = [
            [
                InlineKeyboardButton(
                    "💸 Посмотреть ожидаемый доход",
                    callback_data="weekly_income"
                )],
        ]
        keyboard.extend(moderators_functionality)

    if user_id == int(os.environ["TELEGRAM_ADMIN_ID"]):
        admin_functionality = [
            [
                InlineKeyboardButton(
                    "💸 Посмотреть ожидаемый доход",
                    callback_data="weekly_income"
                )],
            [
                InlineKeyboardButton(
                    "Обновить план на след. неделю",
                    callback_data="update_next_weekly_plan"
                ),
            ]
        ]

        keyboard[-1].append(
            InlineKeyboardButton(
                    "📄 Скорректировать смены",
                    callback_data="change_shift"
                )
        )
        keyboard.extend(admin_functionality)

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = dedent("""
    👋 Привет!
    
    Этот бот поможет тебе узнать, когда смена у Александра. 
    Нажми на кнопку, чтобы узнать план на неделю или же на сегодняшний день.
    """)

    if callback:
        callback.answer()
        callback.edit_message_text(
            text=message,
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(message, reply_markup=reply_markup)

    return States.CHOOSING
