from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class MyCallback(CallbackData, prefix="action"):
    action: str


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Курс Газпромбанка",
                    callback_data=MyCallback(action="show_gz_rate").pack(),
                ),
                InlineKeyboardButton(
                    text="Курс Forex",
                    callback_data=MyCallback(action="show_forex_rate").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Курс ЦБ РФ",
                    callback_data=MyCallback(action="show_cbr_rate").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Включить/Выключить уведомления",
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
                    text="🔙 Назад",
                    callback_data=MyCallback(action="back_to_main_menu").pack(),
                )
            ]
        ]
    )
