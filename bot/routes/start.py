from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from db.session import async_session
from utils.db.user import create_or_update_user
from utils.log import logger
from utils.tl_utils import get_main_menu_keyboard, MyCallback
from schemas.user import UserCreateSchema


start_router = Router()

welcome_message = "Welcome! 🎉\nThis bot helps you check the CNY and USD exchange rate effortlessly.\nSimply choose an option below to get started:"


@start_router.message(Command("start"))
async def main_menu(message: Message):
    user = message.from_user

    async with async_session() as session:
        schema = UserCreateSchema(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            lang=user.language_code,
        )
        await create_or_update_user(session, schema)

    await message.answer(
        welcome_message,
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "back_to_main_menu"))
async def back_to_main_menu(callback_query: CallbackQuery):
    try:
        if callback_query.message.text:
            await callback_query.message.edit_text(
                welcome_message,
                reply_markup=get_main_menu_keyboard(),
            )
        elif callback_query.message.caption or callback_query.message.photo:
            await callback_query.message.delete()
            await callback_query.message.answer(
                welcome_message,
                reply_markup=get_main_menu_keyboard(),
            )
        else:
            await callback_query.message.answer(
                welcome_message,
                reply_markup=get_main_menu_keyboard(),
            )
    except Exception as e:
        logger.error(f"Error in back_to_main_menu: {e}")
        await callback_query.answer("An error occurred while processing your request.")
