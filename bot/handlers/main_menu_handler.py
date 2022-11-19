import os

from textwrap import dedent

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

# TODO Try to fix it later.
import sys
sys.path.append(".")

from bot.conversation_states import States
from bot.database_operations import (check_user_in_database,
                                     save_user_to_database,
                                     get_user_language,
                                     add_language_to_user)


def _english_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Prepare English keyboard for user
    """
    keyboard = [
        [
            InlineKeyboardButton(
                "💥 Current week",
                callback_data="current_week_shifts"
            ),
            InlineKeyboardButton(
                "⏭️ Next week",
                callback_data="next_week_shifts"
            ),
        ],
        [
            InlineKeyboardButton(
                "📅 Today plan",
                callback_data="daily_plan"
            ),
        ],
        [
            InlineKeyboardButton(
                "Change the language / Изменить язык",
                callback_data="change_language"
            )
        ]
    ]

    if user_id == int(os.environ["MODERATORS_TELEGRAM_ID"]):
        moderators_functionality = [
            [
                InlineKeyboardButton(
                    "💸 Expected weekly income",
                    callback_data="weekly_income"
                )],
        ]
        keyboard.extend(moderators_functionality)

    if user_id == int(os.environ["TELEGRAM_ADMIN_ID"]):
        admin_functionality = [
            [
                InlineKeyboardButton(
                    "💸 Expected weekly income",
                    callback_data="weekly_income"
                )],
            [
                InlineKeyboardButton(
                    "Add new shifts",
                    callback_data="update_next_weekly_plan"
                ),
            ]
        ]

        keyboard[-1].append(
            InlineKeyboardButton(
                "📄 Update shifts",
                callback_data="change_shift"
            )
        )
        keyboard.extend(admin_functionality)

    return InlineKeyboardMarkup(keyboard)


def _russian_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Prepare Russian keyboard for user
    """
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
        ],
        [
            InlineKeyboardButton(
                "Изменить язык / Change the language",
                callback_data="change_language"
            )
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

    return InlineKeyboardMarkup(keyboard)


def greeting_block(update: Update, context: CallbackContext):
    """
    Block with user greetings.
    """
    callback = update.callback_query
    if callback:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.message.from_user.id

    if context.user_data["user_language"] == "RU":
        message = dedent("""
        👋 Привет!
    
        Этот бот поможет тебе узнать, когда смена у Александра. 
        Нажми на кнопку, чтобы узнать план на неделю или же на сегодняшний день.
        """)
        reply_markup = _russian_keyboard(user_id)
    else:
        message = dedent("""
        👋 Hello!

        This bot can helps you to check when Alex has shifts. 
        Press the button for check today plan or weekly plans.
        """)
        reply_markup = _english_keyboard(user_id)

    if callback:
        callback.answer()
        callback.edit_message_text(
            text=message,
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            message,
            reply_markup=reply_markup
        )


def register_user(
        update: Update,
        context: CallbackContext) -> States.CHOOSING:
    """
    Register user with preferable language.
    """
    prefer_language, _ = update.callback_query.data.split("_")
    telegram_id = update.callback_query.from_user.id
    add_language_to_user(telegram_id, prefer_language)
    context.user_data["user_language"] = prefer_language
    greeting_block(update, context)
    return States.CHOOSING


def need_register(
        update: Update,
        context: CallbackContext) -> States.CHOOSING:
    """
    Choose language for user.
    """
    if update.callback_query:
        telegram_id = update.callback_query.from_user.id
    else:
        telegram_id = update.message.from_user.id

    user = check_user_in_database(telegram_id=telegram_id)
    if not user:
        save_user_to_database(telegram_id)

    user_language = get_user_language(telegram_id)

    if not user_language:
        message = dedent("""
        🇷🇺  Выберите предпочитаемый язык.
        🇬🇧  Choose your prefer language.
        """)
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🇷🇺 Русский",
                        callback_data="RU_language"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🇬🇧 English",
                        callback_data="EN_language"
                    )
                ]
            ]
        )
        callback = update.callback_query
        if callback:
            callback.answer()
            callback.edit_message_text(
                text=message,
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(message, reply_markup=reply_markup)

        return True

    context.user_data["user_language"] = user_language
    return False


def start(update: Update, context: CallbackContext) -> States:

    if not context.user_data.get("user_language"):
        if need_register(update, context):
            return States.CHOOSING
    greeting_block(update, context)

    return States.CHOOSING
