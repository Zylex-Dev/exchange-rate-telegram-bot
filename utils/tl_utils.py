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
                    text="Notifications",
                    callback_data=MyCallback(action="notifications").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Donate for hosting and a cup of Luckin Coffee",
                    callback_data=MyCallback(action="donate").pack(),
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


def get_notification_config_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Toggle notifications",
                    callback_data=MyCallback(action="show_toggle_notifications").pack(),
                ),
                InlineKeyboardButton(
                    text="Set notifications thresholds",
                    callback_data=MyCallback(action="show_threshold").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back",
                    callback_data=MyCallback(action="back_to_main_menu").pack(),
                )
            ],
        ]
    )


def get_toggle_notifications_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Toggle Gazprombank notifications",
                    callback_data=MyCallback(action="toggle_gz_notify").pack(),
                ),
                InlineKeyboardButton(
                    text="Toggle Google notifications",
                    callback_data=MyCallback(action="toggle_google_notify").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Toggle Central Bank of Russia notifications",
                    callback_data=MyCallback(action="toggle_cbrf_notify").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Toggle all notifications off",
                    callback_data=MyCallback(
                        action="toggle_all_notifications_off"
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back",
                    callback_data=MyCallback(action="back_to_notification_menu").pack(),
                ),
            ],
        ]
    )


def get_threshold_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Set Gazprombank threshold",
                    callback_data=MyCallback(action="set_gz_threshold").pack(),
                ),
                InlineKeyboardButton(
                    text="Set Google threshold",
                    callback_data=MyCallback(action="set_google_threshold").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Set Central Bank of Russia threshold",
                    callback_data=MyCallback(action="set_cbrf_threshold").pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back",
                    callback_data=MyCallback(action="back_to_notification_menu").pack(),
                ),
            ],
        ]
    )
