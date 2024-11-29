from logging import getLogger
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from typing import Tuple, Optional

from db.session import async_session
from utils.db.user import (
    create_or_update_user,
    update_user,
    get_user_by_id,
    update_user_alert_rate,
)
from utils.tl_utils import (
    get_main_menu_keyboard,
    get_back_to_main_menu_keyboard,
    MyCallback,
)
from utils.gz_utils import get_gz_exchange_rate
from schemas.user import UserCreateSchema, UserUpdateSchema


log = getLogger("bot")

start_router = Router()


@start_router.message(Command("start"))
async def index(message: Message):
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
        "Приветствую! Это бот по просмотру курса обмена валют, выберете желаемую опцию:",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "show_gz_rate"))
async def show_gz_rate(callback_query: CallbackQuery):
    user = callback_query.from_user
    async with async_session() as session:
        values: Optional[Tuple] = await get_gz_exchange_rate()
        if values is not None:
            buy_rate, sell_rate, rate_date = values
            await update_user_alert_rate(session, user.id, buy_rate)
            await callback_query.message.edit_text(
                f"🈸CNY Exchange Rate:\n💹Buy: {buy_rate}₽, Sell: {sell_rate}₽\n🕐Date: {rate_date}",
                reply_markup=get_back_to_main_menu_keyboard(),
            )
        else:
            await callback_query.message.edit_text(
                f"В настоящее время нельзя получить данные по курсу...",
                reply_markup=get_back_to_main_menu_keyboard(),
            )


@start_router.callback_query(MyCallback.filter(F.action == "show_forex_rate"))
async def show_forex_rate(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Скоро появится...",
        reply_markup=get_back_to_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "show_cbr_rate"))
async def show_cbr_rate(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Скоро появится...",
        reply_markup=get_back_to_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "back_to_main_menu"))
async def back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Приветствую! Это бот по просмотру курса обмена валют, выберете желаемую опцию:",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "toggle_notify"))
async def toggle_notify(callback_query: CallbackQuery):
    user = callback_query.from_user

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)

        if user_data is None:
            await callback_query.answer(
                "Ошибка: пользователь не найден в базе данных.", show_alert=True
            )
            return

        new_notify_value = not user_data.get("notify", False)

        schema = UserUpdateSchema(id=user.id, notify=new_notify_value)

        await update_user(session, schema)
        log.info(
            "User with id {} toggled {} their notifications".format(
                user.id, "on" if new_notify_value else "off"
            )
        )
        await callback_query.message.edit_text(
            f"Уведомления {'включены' if new_notify_value else 'выключены'}.",
            reply_markup=get_back_to_main_menu_keyboard(),
        )
