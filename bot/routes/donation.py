import os
from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InputMediaPhoto,
    FSInputFile,
)

from utils.log import logger
from utils.tl_utils import get_back_to_main_menu_keyboard, MyCallback


donation_router = Router()


@donation_router.callback_query(MyCallback.filter(F.action == "donate"))
async def handle_donate(callback_query: CallbackQuery):
    qr_code_path = os.path.join(os.getcwd(), "data/other/qr-code.jpg")
    if os.path.exists(qr_code_path):
        qr_code_file = FSInputFile(qr_code_path)

        await callback_query.message.edit_media(
            media=InputMediaPhoto(
                media=qr_code_file,
                caption=(
                    "To make a donation:\n"
                    "- *For RUB*: Use the number `+79991728881`.\n"
                    "- *For CNY*: Scan the QR code above."
                ),
            ),
            reply_markup=get_back_to_main_menu_keyboard(),
        )
    else:
        await callback_query.message.edit_text(
            text=(
                "To make a donation:\n" "- *For RUB*: Use the number `+79991728881`.\n"
            ),
            reply_markup=get_back_to_main_menu_keyboard(),
        )

    user = callback_query.from_user
    logger.info(f"User {user.id} requested donation information.")
