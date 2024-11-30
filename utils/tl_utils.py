from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class MyCallback(CallbackData, prefix="action"):
    action: str


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Gazprombank",
                    callback_data=MyCallback(action="show_gz_rate").pack(),
                ),
                InlineKeyboardButton(
                    text="Google",
                    callback_data=MyCallback(action="show_google_rate").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Central Bank of Russia",
                    callback_data=MyCallback(action="show_cbr_rate").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Toggle notifications",
                    callback_data=MyCallback(action="toggle_notify").pack(),
                ),
            ],
        ]
    )


def get_back_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Back",
                    callback_data=MyCallback(action="back_to_main_menu").pack(),
                )
            ]
        ]
    )
